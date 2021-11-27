import hassapi as hass
import datetime


class AreaDevice(hass.Hass):

    async def initialize(self):
        await self.init_area()
        await self.init_device()

    async def init_area(self):
        self.area = None
        area_name = self.args.get("area_name")
        if area_name:
            self.area = await self.get_app(area_name)
            if not self.area:
                self.log("Area not initialized, {}".format(area_name))
        else:
            pass

    async def init_device(self):
        device_ieee = self.args.get("device_ieee")
        self.event_listen_handle = await self.listen_event(
            self.event_cb,
            "zha_event",
            device_ieee=device_ieee
        )

    async def terminate(self):
        await self.cancel_listen_event(self.event_listen_handle)


class AreaButton(AreaDevice):

    async def initialize(self):
        await super().initialize()
        await self.init_dimmer()
        self.dim_interval_s = 0.2

    async def init_dimmer(self):
        self.dimmer_timer_handle = None

    async def event_cb(self, event_name, data, kwargs):
        if not "command" in data:
            return
        
        command = data["command"]
        time_fired = datetime.datetime.fromisoformat(data["metadata"]["time_fired"])

        await self.cancel_dimmer_timer()
        if command == "on":
            await self.area.service_manual("on", time_fired)
        elif command == "off":
            await self.area.service_manual("off", time_fired)
        elif command == "move_with_on_off":
            self.dimmer_timer_handle = await self.run_every(
                self.dim_up,
                "now",
                self.dim_interval_s
            )
        elif command == "move":
            self.dimmer_timer_handle = await self.run_every(
                self.dim_down,
                "now",
                self.dim_interval_s
            )
        elif command == "stop":
            pass

    async def cancel_dimmer_timer(self):
        if self.dimmer_timer_handle != None:
            await self.cancel_timer(self.dimmer_timer_handle)
            self.dimmer_timer_handle = None

    async def dim_up(self, kwargs):
        if self.area:
            time_fired = datetime.datetime.now(datetime.timezone.utc)
            await self.area.service_manual("dim_up", time_fired)

    async def dim_down(self, kwargs):
        if self.area:
            time_fired = datetime.datetime.now(datetime.timezone.utc)
            await self.area.service_manual("dim_down", time_fired)

    async def terminate(self):
        await super().terminate()


class AreaDoorSensor(AreaDevice):

    async def initialize(self):
        await super().initialize()

    async def event_cb(self, event_name, data, kwargs):
        if not "command" in data:
            return
        
        command = data["command"]
        args = data["args"]
        time_fired = datetime.datetime.fromisoformat(data["metadata"]["time_fired"])

        if command == "attribute_updated" and args["attribute_name"] == "on_off":
            if args["value"] == 1:
                await self.area.service_automated("on", time_fired)
            if args["value"] == 0:
                await self.area.service_automated("off", time_fired)

    async def terminate(self):
        await super().terminate()
