import copy
import logging

from django.apps import apps

from share import disambiguation


logger = logging.getLogger(__name__)


class GraphParsingException(Exception):
    pass


class CyclicalDependency(GraphParsingException):
    pass


class UnresolvableReference(GraphParsingException):
    pass


class ChangeNode:

    @classmethod
    def from_jsonld(self, ld_graph, disambiguate=True, extra_namespace=None):
        return ChangeNode(ld_graph, disambiguate=disambiguate, extra_namespace=extra_namespace)

    @property
    def model(self):
        if self.is_merge:
            return apps.get_model('share', self.relations['into']['@type'].lower())
        return apps.get_model('share', self.type.lower())

    @property
    def instance(self):
        return self.__instance

    @instance.setter
    def instance(self, instance):
        if instance:
            self.id = instance.pk
            self.type = instance._meta.model_name.lower()
            self.__refs.append((self.id, self.type))
        self.__instance = instance

    @property
    def is_blank(self):
        # JSON-LD Blank Node ids start with "_:"
        return self.is_merge or (isinstance(self.id, str) and self.id.startswith('_:'))

    @property
    def is_merge(self):
        return self.type.lower() == 'mergeaction'

    @property
    def ref(self):
        return {'@id': self.id, '@type': self.type}

    @property
    def refs(self):
        return self.__refs

    @property
    def change(self):
        if self.is_merge:
            return {**self.attrs, **self.relations, **self._reverse_relations}

        if self.is_blank:
            ret = {**self.attrs, **self.relations}
            if self.extra:
                ret['extra'] = self.extra
            return ret

        if not self.instance:
            raise UnresolvableReference('@id: {!r}, @type: {!r}'.format(self.id, self.type))

        ret = {k: v for k, v in self.attrs.items() if getattr(self.instance, k) != v}
        if self.__extra_namespace:
            ret['extra'] = {
                k: v for k, v in self.extra.items()
                if not (self.instance.extra and self.instance.extra.get(self.__extra_namespace))
                or self.instance.extra.data[self.__extra_namespace].get(k) != v
            }

            if not ret['extra']:
                del ret['extra']

        new_type = self.__refs[0][1]
        if new_type != self.type and new_type != 'creativework':
            ret['@type'] = new_type

        return ret

    def __init__(self, node, disambiguate=True, extra_namespace=None):
        self.__raw = node
        self.__change = None
        self.__instance = None
        self.__extra_namespace = None
        node = copy.deepcopy(self.__raw)

        self.id = str(node.pop('@id'))
        self.type = node.pop('@type').lower()
        self.extra = node.pop('extra', {})

        self.__refs = [(self.id, self.type)]

        # JSON-LD variables are all prefixed with '@'s
        self.context = {k: node.pop(k) for k in tuple(node.keys()) if k[0] == '@'}
        # Any nested data type is a relation in the current JSON-LD schema
        self.relations = {k: node.pop(k) for k, v in tuple(node.items()) if isinstance(v, dict)}
        self.related = tuple(self.relations.values())

        self.reverse_relations = {}  # Resolved through relations to be populated later
        self.__reverse_relations = {k: tuple(node.pop(k)) for k, v in tuple(node.items()) if isinstance(v, (list, tuple))}

        self.attrs = node

        if disambiguate:
            self._disambiguate()

    def resolve_relations(self, mapper):
        for key, relations in self.__reverse_relations.items():
            resolved = [
                next(x for x in mapper[r['@id'], r['@type'].lower()].related if x['@id'] != self.id)
                for r in relations
            ]
            self.reverse_relations[key] = resolved
            self.related += tuple(resolved)

    def update_relations(self, mapper):
        for v in self.relations.values():
            try:
                node = mapper[(v['@id'], v['@type'].lower())]
                v['@id'] = node.id
                v['@type'] = node.type
            except KeyError:
                pass
        for k, values in self.reverse_relations.items():
            self.reverse_relations[k] = [mapper.get((v['@id'], v['@type'].lower()), (v['@id'], v['@type'].lower())).ref for v in values]

    def _disambiguate(self):
        if self.is_merge:
            return None

        self.instance = disambiguation.disambiguate(self.id, {
            **self.attrs,
            **{k: v['@id'] for k, v in self.relations.items() if not str(v['@id']).startswith('_:')},
            **{k: [x['@id'] for x in v if not str(x['@id']).startswith('_:')] for k, v in self.reverse_relations.items() if any(not str(x['@id']).startswith('_:') for x in v)},
        }, self.model)

    def __repr__(self):
        return '<{}({}, {})>'.format(self.__class__.__name__, self.model, self.instance)


class ChangeGraph:

    @classmethod
    def from_jsonld(self, ld_graph, disambiguate=True, extra_namespace=None):
        nodes = [ChangeNode.from_jsonld(obj, disambiguate=False, extra_namespace=extra_namespace) for obj in ld_graph['@graph']]
        return ChangeGraph(nodes, disambiguate=disambiguate)

    @property
    def nodes(self):
        return self.__nodes

    def __init__(self, nodes, parse=True, disambiguate=True):
        self.__nodes = nodes
        self.__map = {ref: n for n in nodes for ref in n.refs}
        self.__sorter = NodeSorter(self)

        for node in self.__nodes:
            node.resolve_relations(self.__map)

        if parse:
            self.__nodes = self.__sorter.sorted()

        # TODO This could probably be more efficiant
        if disambiguate:
            for n in self.__nodes:
                n.update_relations(self.__map)
                n._disambiguate()
                for ref in n.refs:
                    self.__map[ref] = n

    def get_node(self, id, type):
        try:
            return self.__map[(id, type.lower())]
        except KeyError:
            if str(id).startswith('_:'):
                raise UnresolvableReference('Unresolvable reference @id: {!r}, @type: {!r}'.format(id, type))
        return None  # External reference to an already existing object


class NodeSorter:

    def __init__(self, graph):
        self.__sorted = []
        self.__graph = graph
        self.__visted = set()
        self.__visiting = set()
        self.__nodes = list(graph.nodes)

    def sorted(self):
        if not self.__nodes:
            return self.__sorted

        while self.__nodes:
            n = self.__nodes.pop(0)
            self.__visit(n)

        return self.__sorted

    def __visit(self, node):
        if node in self.__visiting:
            raise CyclicalDependency(node, self.__visiting)

        if node in self.__visted:
            return

        self.__visiting.add(node)
        for relation in node.related:
            n = self.__graph.get_node(relation['@id'], relation['@type'])
            if n:
                self.__visit(n)

        self.__visted.add(node)
        self.__sorted.append(node)
        self.__visiting.remove(node)
