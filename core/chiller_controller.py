from core.temperature_control import TemperatureController

class ChillerController():
    def __init__(self, banks, comports={2701:"COM21", 2702:"COM19", 5201:"COM3", 5202:"COM5", 5801:{"1-4":"COM18", "5-8":"COM4"}, 5802:"COM20", 5901:"COM25", 5902:"COM7"}):
        #initialize with list of banks that should be controlled
        #comports can be either:
        # - {bank: "COMx"} for a single chiller per bank (legacy behavior)
        # - {bank: {"1-4": "COMx", "5-8": "COMy"}} for split groups per bank
        self.group_keys = ("1-4", "5-8")
        self.chillers = {}  #dictionary containing objects for the chillers
        for bank in banks:
            if bank not in comports.keys():
                return f"Bank {bank} does not have associated comport"
            port_map = comports.get(bank)
            if isinstance(port_map, dict):
                # validate provided groups and build controllers per group
                missing = [g for g in self.group_keys if g not in port_map]
                if missing:
                    return f"Bank {bank} missing group comports for {missing}"
                self.chillers.update({
                    bank: {
                        self.group_keys[0]: TemperatureController(port_map[self.group_keys[0]]),
                        self.group_keys[1]: TemperatureController(port_map[self.group_keys[1]])
                    }
                })
            else:
                # legacy single-port per bank
                self.chillers.update({bank: TemperatureController(port_map)})
    
    def set_temp(self, bank, temp, group=None):
        if bank not in self.chillers:
            return "Invalid bank number"
        controller = self.chillers[bank]
        if isinstance(controller, dict):
            if group is None:
                return f"Bank {bank} is configured with multiple comports; specify group as '1-4' or '5-8'"
            if group not in controller.keys():
                return f"Invalid group '{group}' for bank {bank}; valid groups are {list(controller.keys())}"
            return controller[group].set_temperature(temp)
        else:
            # single controller; ignore group if provided
            return controller.set_temperature(temp)
    
    def read_temp(self, bank, group=None):
        if bank not in self.chillers:
            return "Invalid bank number"
        controller = self.chillers[bank]
        if isinstance(controller, dict):
            if group is None:
                return f"Bank {bank} is configured with multiple comports; specify group as '1-4' or '5-8'"
            if group not in controller.keys():
                return f"Invalid group '{group}' for bank {bank}; valid groups are {list(controller.keys())}"
            return controller[group].read_temperature()
        else:
            # single controller; ignore group if provided
            return controller.read_temperature()
    
    def get_port(self, bank, group=None):
        # utility to fetch the underlying port string(s) for error messages
        if bank not in self.chillers:
            return None
        controller = self.chillers[bank]
        try:
            # TemperatureController stores serial_port after open; we keep original port in .port
            if isinstance(controller, dict):
                if group is None:
                    return {g: controller[g].port for g in controller}
                if group in controller:
                    return controller[group].port
                return None
            else:
                return controller.port
        except Exception:
            return None
