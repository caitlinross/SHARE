import logging

import arrow

from share.bot import Bot
from share.change import ChangeNode
from share.models import CeleryProviderTask

from share.models import Tag

logger = logging.getLogger(__name__)


class AutoCurateBot(Bot):

    def run(self, last_run, dry=False):
        if not last_run:
            logger.debug('Finding last successful job')
            last_run = CeleryProviderTask.objects.filter(
                app_label=self.config.label,
                status=CeleryProviderTask.STATUS.succeeded,
            ).order_by(
                '-timestamp'
            ).values_list('timestamp', flat=True).first()
            if last_run:
                last_run = arrow.get(last_run)
            else:
                last_run = arrow.get(0)
            logger.info('Found last job %s', last_run)
        else:
            last_run = arrow.get(last_run)

        logger.info('Using last run of %s', last_run)
        self.do_curation(last_run)

    def do_curation(self, last_run: arrow.Arrow):
        submitted = set()

        qs = Tag.objects.filter(
            date_modified__gte=last_run.datetime,
        )

        total = qs.count()
        logger.info('Found %s tags eligible for automatic curation', total)

        for tag in qs:
            if tag.id in submitted:
                continue

            matches = list(
                Tag.objects.filter(
                    name__iexact=tag.name,
                ).order_by('-date_modified').values_list('id', flat=True)
            )

            if len(matches) > 1:
                submitted = submitted.union(set(matches))
                # use the oldest record from the order by specified
                into_id = matches.pop()
                json_ld = {
                    '@id': '_:{}'.format(into_id),
                    '@type': 'MergeAction',
                    'into': {'@type': 'Person', '@id': into_id},
                    'from': []
                }
                for from_id in matches:
                    json_ld['from'].append({'@type': 'Person', '@id': from_id})
                ChangeNode.from_jsonld(json_ld, disambiguate=False)
                logger.info('Created changeset for tag %s (%d) found %d matche(s)', tag, into_id, len(matches))
