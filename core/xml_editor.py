import xml.etree.ElementTree as ET

class profile_editor:
    #class to allow direct editing of parameters in Neware XML profiles
    def __init__(self, filepath):
        self.prsr = ET.XMLParser(encoding="utf-8")
        self.filepath = filepath
        self.factors = {}
        self.scale = 100    #default scale factor, automatically updated when XML is opened
        self.open_file(filepath)

    def open_file(self, filepath):
        self.tree = ET.parse(filepath, parser=self.prsr)
        self.root = self.tree.getroot()
        for match in self.root.iter('Scale'):
            self.scale = int(match.get('Value'))
        self.update_factors()

    def update_factors(self):
        self.factors['Volt'] = 10000                        #voltages stored in tenths of mV
        self.factors['Curr'] = 1000 * self.scale            #currents stored in mA, scaled by global factor
        self.factors['Pow'] = 1000 * self.scale              #powers stored in mW, scaled by global factor
        self.factors['Stop_Volt'] = 10000                    #stop voltages stored in tenths of mV
        self.factors['Stop_Curr'] = 1000 * self.scale        #stop currents stored in mA, scaled by global factor
        self.factors['Cap'] = 3600 * 1000 * self.scale      #capacity stored in mAs, scaled by global factor
        self.factors['Time'] = 1000                          #time stored in ms
        return self.factors

    def get_current_params(self, params_to_get):
        """accepts a dictionary of parameters to get, with each entry in the form
        "human readable param name": ["step#", "keyword"] and returns a dictionary of the current values. 
        Valid keywords are Volt, Curr, Pow, Cap, Stop_Curr, Stop_Volt, Time"""
        current_params = {}
        for key, val in params_to_get.items():
            stepname = val[0]
            keywordname = val[1]
            for step in self.root.iter(stepname):       #go through all steps and look for matched string
                for keyword in step.find('Limit').iter(keywordname):      #go through all the lines in the limits section and looks for the keyword
                    current_params[key] = float(keyword.get('Value')) / (self.factors.get(keyword.tag, 1))
        return current_params

    def update_test_profile_params(self, params_to_edit, new_params):
            """accepts a dictionary of parameters to edit, with each entry in the form
            "human readable param name": ["step#", "keyword"] and dicctionary of new values for those parameters. 
        Valid keywords are Volt, Curr, Pow, Cap, Stop_Curr, Stop_Volt, Time"""
            params_updated = 0
            for key, val in params_to_edit.items():
                stepname = val[0]
                keywordname = val[1]
                for step in self.root.iter(stepname):       #go through all steps and look for matched string
                    for keyword in step.find('Limit').iter(keywordname):      #go through all the lines in the limits section and looks for the keyword
                        val_from_user = new_params.get(key)
                        if val_from_user is None:
                            raise Exception("missing new parameter")
                        else:
                            newval = str(int(float(val_from_user) * self.factors.get(keyword.tag, 1)))  #default factor is 1
                            keyword.set('Value', newval)
                            params_updated = params_updated + 1
            self.tree.write(self.filepath)
            return params_updated
    