import areaDevice
import datetime


class AreaButton(areaDevice.AreaDevice):

    async def initialize(self):
        await super().initialize()
        await self.init_dimmer()
        self.dim_interval_s = 0.2

    async def init_dimmer(self):
        self.dimmer_timer_handle = None

    async def event_cb(self, event_name, data, kwargs):
        command = data["command"]
        time_fired = datetime.datetime.fromisoformat(data["metadata"]["time_fired"])

        await self.cancel_dimmer_timer()
        if command == "on":
            await self.area.service_manual(time_fired, "on")
        elif command == "off":
            await self.area.service_manual(time_fired, "off")
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
            await self.area.service_manual(time_fired, "dim_up")

    async def dim_down(self, kwargs):
        if self.area:
            time_fired = datetime.datetime.now(datetime.timezone.utc)
            await self.area.service_manual(time_fired, "dim_down")

    async def terminate(self):
        await super().terminate()
