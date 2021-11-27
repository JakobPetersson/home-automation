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
        await self.init_click()
        await self.init_dimmer()

    async def init_click(self):
        self.click_cb_handle = None
        await self.click_reset()

    async def init_dimmer(self):
        self.dimmer_timer_handle = None
        self.dimmer_interval_s = 0.2

    async def event_cb(self, event_name, data, kwargs):
        if not "command" in data:
            return
        
        command = data["command"]
        time_fired = datetime.datetime.fromisoformat(data["metadata"]["time_fired"])

        await self.cancel_dimmer_timer()
        if command == "on":
            await self.click_register(command, time_fired)
        elif command == "off":
            await self.click_register(command, time_fired)            
        elif command == "move_with_on_off":
            await self.click_reset()
            self.dimmer_timer_handle = await self.run_every(
                self.dim_up,
                "now",
                self.dimmer_interval_s
            )
        elif command == "move":
            await self.click_reset()
            self.dimmer_timer_handle = await self.run_every(
                self.dim_down,
                "now",
                self.dimmer_interval_s
            )
        elif command == "stop":
            await self.click_reset()

    #
    # Register a click.
    # Always act on first click of its kind as a single click to feel responsive.
    # Multi-click will be handled later.
    #
    async def click_register(self, command, time_fired):
        if command != self.click_command:
            # Reset if new command
            await self.click_reset()

            # Always  act on first click
            await self.click_do(command, time_fired)

            # Start counting again
            self.click_command = command
            self.click_time_fired = time_fired

        # Increment count
        self.click_count+=1

        # Cancel and schedule new callback
        await self.click_cb_cancel()
        await self.click_cb_schedule()
        
    #
    # Reset click logic
    #
    async def click_reset(self):
        self.click_command = None
        self.click_time_fired = None
        self.click_count = 0
        await self.click_cb_cancel()

    #
    # Cancel click callback if active
    #    
    async def click_cb_cancel(self):
        if self.click_cb_handle != None:
            await self.cancel_timer(self.click_cb_handle)
            self.click_cb_handle = None

    #
    # Schedule new click callback
    #
    async def click_cb_schedule(self):
        self.click_cb_handle = await self.run_every(
            self.click_cb,
            "now+2",
            10
        )

    #
    # Click callback
    #
    async def click_cb(self, kwargs):
        # Always cancel further callbacks if we reach it (timed out)
        await self.click_cb_cancel()
        
        if self.click_count > 1:
            # Only handle multi-clicks
            await self.click_do(self.click_command, self.click_time_fired, self.click_count)

        # Reset after handling
        await self.click_reset()

    #
    # Do something when a click happens
    #
    async def click_do(self, command, time_fired, count=1):
        if count == 1:
            if command == "on":
                await self.area.service_manual("on", time_fired)
            elif command == "off":
                await self.area.service_manual("off", time_fired)

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
