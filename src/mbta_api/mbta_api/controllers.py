from .api import Vehicle

class BaseController:
    def __init__(self, map_type, config):
        self.mbta_map = map_type(config)

    def draw_loop(self, count, vehicles):
        raise NotImplementedError()


class SimpleController(BaseController):
    def draw_loop(self, count, vehicles):
        self.mbta_map.turn_off_all()
        for vehicle in vehicles:
            if not vehicle.stop or not vehicle.stop.isdigit():
                # There's some weird stops at the ends of lines like "Oak-Grove-02. Maybe an intermediate state before it turns around"
                # also the stop may potentially be None - if the vehicle is out of service
                continue
            if vehicle.direction:
                color = 0xFF0000
            else:
                color = 0x00FF00

            local_id = self.mbta_map.get_mapid(vehicle.stop)
            if not local_id:
                logging.error(f"Unmapped MBTA ID {vehicle.stop}")
                continue

            current_mappoint = self.mbta_map.get_mappoint(local_id)
            color = color | current_mappoint.color

            if vehicle.status == Vehicle.Status.STOPPED_AT:
                self.mbta_map.update_mappoint(local_id, color, 1.0)
            elif count %2:
                self.mbta_map.update_mappoint(local_id, color, 1.0)
        self.mbta_map.update()


class AlternatingController(BaseController):
    def draw_loop(self, count, vehicles):
        self.mbta_map.turn_off_all()
        for vehicle in vehicles:
            if not vehicle.stop or not vehicle.stop.isdigit():
                # There's some weird stops at the ends of lines like "Oak-Grove-02. Maybe an intermediate state before it turns around"
                # also the stop may potentially be None - if the vehicle is out of service
                continue

            if vehicle.direction:
                if count % 10 < 5:
                    color = 0xFF0000
                else:
                    continue
            else:
                if count % 10 >= 5:
                    color = 0x00FF00
                else:
                    continue

            local_id = self.mbta_map.get_mapid(vehicle.stop)
            if not local_id:
                logging.error(f"Unmapped MBTA ID {vehicle.stop}")
                continue

            current_mappoint = self.mbta_map.get_mappoint(local_id)
            color = color | current_mappoint.color

            if vehicle.status == Vehicle.Status.STOPPED_AT:
                self.mbta_map.update_mappoint(local_id, color, 1.0)
            else:
                self.mbta_map.update_mappoint(local_id, 0xFFFF00, 1.0)
        self.mbta_map.update()

class ZenController(BaseController):
    def draw_loop(self, count, vehicles):
        raise NotImplementedError()
