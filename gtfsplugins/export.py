# -*- coding: utf-8 -*-
#    This file is part of Gtfslib-python.
#
#    Gtfslib-python is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Gtfslib-python is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with gtfslib-python.  If not, see <http://www.gnu.org/licenses/>.
"""
@author: Laurent GRÉGOIRE <laurent.gregoire@mecatran.com>
"""

from gtfslib.utils import fmttime
from gtfsplugins.prettycsv import PrettyCsv

class GtfsExport(object):
    """
    Export some data in GTFS-compatible format.
    For now only export stop times (stop_times.txt file) and calendar
    dates (calendar_dates.txt file).
    Be careful, the interface of this plugin may change in the future!

    Parameters:
    --skip_shape_dist   To remove shape_dist_traveled from the export.

    Examples:
    --filter="(Route.route_short_name=='R1')"
      Restrict to route R1
    """

    def __init__(self):
        pass

    def run(self, context, skip_shape_dist=False, **kwargs):

        stop_times_columns = ["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence", "stop_headsign", "pickup_type", "drop_off_type", "timepoint"]
        if not skip_shape_dist:
            stop_times_columns.append("shape_dist_traveled")
        with PrettyCsv("stop_times.txt", stop_times_columns, **kwargs) as csvout:
            ntrips = 0
            for trip in context.dao().trips(fltr=context.args.filter, prefetch_stops=False, prefetch_stop_times=True, prefetch_calendars=False, prefetch_routes=False):
                ntrips += 1
                if ntrips % 1000 == 0:
                    print("%d trips..." % (ntrips))
                for stoptime in trip.stop_times:
                    row = [ trip.trip_id,
                            fmttime(stoptime.arrival_time if stoptime.arrival_time else stoptime.departure_time),
                            fmttime(stoptime.departure_time if stoptime.departure_time else stoptime.arrival_time),
                            stoptime.stop_id,
                            stoptime.stop_sequence,
                            stoptime.stop_headsign,
                            stoptime.pickup_type,
                            stoptime.drop_off_type,
                            stoptime.timepoint ]
                    if not skip_shape_dist:
                        row.append(stoptime.shape_dist_traveled)
                    csvout.writerow(row)
            print("Exported %d trips" % (ntrips))

        with PrettyCsv("calendar_dates.txt", ["service_id", "date", "exception_type"], **kwargs) as csvout:
            ncals = ndates = 0
            for calendar in context.dao().calendars(fltr=context.args.filter, prefetch_dates=True):
                ncals += 1
                if ncals % 1000 == 0:
                    print("%d calendars, %d dates..." % (ncals, ndates))
                for date in calendar.dates:
                    ndates += 1
                    csvout.writerow([calendar.service_id, date.toYYYYMMDD(), 1])
            print("Exported %d calendars with %d dates" % (ncals, ndates))