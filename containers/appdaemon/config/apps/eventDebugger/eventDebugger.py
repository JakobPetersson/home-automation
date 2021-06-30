import hassapi as hass

class EventDebugger(hass.Hass):

        def initialize(self):
                self.event_listen_handle = self.listen_event(self.event_cb)

        def event_cb(self, event_name, data, kwargs):
                self.log("Event name: {}".format(event_name))
                self.log("Event data: {}".format(data))

        def terminate(self):
                self.cancel_listen_event(self.event_listen_handle)
