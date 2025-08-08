import midas.client
import midas
import midas.frontend
import midas.event

import collections

#from wms_midas.utilities import ELLxConnection
from StageControl.ELLxControl import ELLxConnection

class ELLxStageMidas(midas.frontend.EquipmentBase, ELLxConnection):
    def __init__(self, client: midas.client.MidasClient, usb_path):
        devName = "ELLXStage"
        equip_name = "ELLXStage"

        default_common = midas.frontend.InitialEquipmentCommon()
        default_common.equip_type = midas.EQ_PERIODIC
        default_common.buffer_name = "SYSTEM"
        default_common.trigger_mask = 0
        default_common.event_id = 16
        default_common.period_ms = 10000 # not really doing anything...
        default_common.read_when = midas.RO_ALWAYS
        default_common.log_history = 60 #NOT SURE IF THIS MUST BE UNIQUE 

        default_settings = collections.OrderedDict([  
            ("dev",devName),

        ]) 
        self.client = client 

        midas.frontend.EquipmentBase.__init__(self, client, equip_name, default_common, default_settings)


        ELLxConnection.__init__(self, usb_path)

    def detailed_settings_changed_func(self, path, idx, new_value):
        if path=="/Equipment/ELLxStage/Settings/destination":
            new_path = "/Equipment/ELLxStage/Variables/destination"
            self.move_absolute(new_value)
            new_destination= self.get_position()
            self.client.odb_set(new_path+"[{}]".format(idx),new_destination,False ,resize_arrays=False)
        else: 
            self.client.msg("No handler for {}".format(path))

class feStage(midas.frontend.FrontendBase):
    def __init__(self, stagemidas:ELLxStageMidas):
        midas.frontend.FrontendBase.__init__(self, "feButtonManager")
        
        self.add_equipment(stagemidas(self.client))

        # these can be changed by the user 
        self.client.odb_watch("/Equipment/ELLxStage/Settings/destination",self.update_position)

    def update_position(self):
        pass 