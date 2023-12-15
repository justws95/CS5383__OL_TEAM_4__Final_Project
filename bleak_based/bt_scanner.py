# Imports
import asyncio

from tkinter import *
from bleak import BleakScanner, BleakClient, BleakError


# Constants
DEFAULT_CONNECTION_DICT = {
    "MAC": None,
    "Services": None,
    "Characteristics": None,
    "Descriptors": None, 
    "Characteristics_Values": []
}

IS_VERBOSE = True


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)        
        self.master = master
        self.button_map = {}
        self.active_BLE_client_info  = DEFAULT_CONNECTION_DICT

        self.pack(fill=BOTH, expand=1)

        # Scan button
        scanButton = Button(self, text="Scan for Devices", command=self.scanForBTdevices)
        scanButton.pack(side=TOP)
        self.button_map['scan_button'] = scanButton

        # Device list
        self.nearby_devices_view = Listbox(self, width=100)
        self.nearby_devices_view.pack(side=TOP)
        self.is_initial_scan = True

        # Display selected device
        display_selection_button = Button(self, text='Conect to Device', width=15, height=2, command=self.view_device_details)
        display_selection_button.pack(side=TOP)

        self.selected_device = StringVar(self, "No Device Selected")
        selection_label = Label(self, font=('Arial', 10), textvariable=self.selected_device)
        selection_label.pack(side=LEFT)

        # Exit Program
        exitButton = Button(self, text="Exit Application", command=self.clickExitButton)
        exitButton.pack(side=BOTTOM)
        self.button_map['exit_button'] = exitButton


    # Exit Program function
    def clickExitButton(self):
        exit()


    # Scan local area for BLE devices
    def scanForBTdevices(self):
        # Perform the scan
        self.button_map['scan_button'].configure(text="Scanning...")
        asyncio.run(self.scan_for_BLE_devices(verbose=IS_VERBOSE))

        # Rename the button
        self.button_map['scan_button'].configure(text="Perform Scan Again")


    # Print selected device
    def view_device_details(self):
        msg_value = None

        try:
            if self.nearby_devices_view.curselection():
                device_selection = self.nearby_devices_view.get(self.nearby_devices_view.curselection()) 
                msg_str = "Connected to: "
                msg_str += device_selection
                msg_value = msg_str
                self.create_device_info_window(selected_device=device_selection)
            else:
                msg_value = "ERROR: No Device Selected"  
        except:
            msg_value = "ERROR: Unhandled exception thrown while selecting device" 
            return

        self.selected_device.set(msg_value)


    # Parse device address from name string
    def parse_device_address_from_str(self, device_str, verbose=IS_VERBOSE):
        MAC_ADDR = device_str[:device_str.rfind(':')]

        if verbose:
            print(f"MAC_ADDR==> <{MAC_ADDR}>")

        return MAC_ADDR
    

    # Helper to close out a device conncetion
    def close_device_connection_window(self):
        # Reset the connection info dictionary
        self.active_BLE_client_info = DEFAULT_CONNECTION_DICT

        # Update device selection display
        self.selected_device.set("No Device Selected")

        # Destroy the connection window
        self.connection_window.destroy()
        

    # Open new window for the conected device
    def create_device_info_window(self, selected_device):
        # Parse the MAC address from the name str
        MAC_ADDR = self.parse_device_address_from_str(selected_device, verbose=IS_VERBOSE)
        try:
            asyncio.run(self.connect_to_selected_BLE_device(MAC_ADDR=MAC_ADDR, verbose=IS_VERBOSE))
        except:
            self.selected_device.set("Exception thrown while attempting device connection!")
        
        # Create the new window
        self.connection_window = Toplevel(self.master)
    
        # Set window Title
        self.connection_window.title(f"BLE Device MAC Address: <{MAC_ADDR}>")
    
        # sets the geometry of toplevel
        self.connection_window.geometry("600x600")

        # Populate services list
        services_label = Label(self.connection_window, font=('Arial', 10), text="Services:")
        services_label.pack(side=TOP)

        services_info_box = Listbox(self.connection_window, width=100)
        services_info_box.pack(side=TOP)

        counter = 1
        for service in self.active_BLE_client_info["Services"]:
            services_info_box.insert(counter, service)
            counter += 1
        counter = 0

        # Populate characteristics list
        characteristics_label = Label(self.connection_window, font=('Arial', 10), text="Characteristics:")
        characteristics_label.pack(side=TOP)
        
        characteristics_info_box = Listbox(self.connection_window, width=100)
        characteristics_info_box.pack(side=TOP)

        counter = 1
        
        for characteristic in self.active_BLE_client_info["Characteristics"]:
            insert_str = str(characteristic)
            characteristics_info_box.insert(counter, insert_str)
            counter += 1

        counter = 0

        # Populate descriptors list
        descriptors_label = Label(self.connection_window, font=('Arial', 10), text="Descriptors:")
        descriptors_label.pack(side=TOP)
        
        descriptors_info_box = Listbox(self.connection_window, width=100)
        descriptors_info_box.pack(side=TOP)

        counter = 1
        for descriptor in self.active_BLE_client_info["Descriptors"]:
            descriptors_info_box.insert(counter, descriptor)
            counter += 1
        counter = 0


        # Close out the connection info screen
        close_connection_button = Button(self.connection_window, text="Close Connection Info", command=self.close_device_connection_window)
        close_connection_button.pack(side=BOTTOM)

    
    ######## Bleak Helper Methods ########

    # Scan for BLE devices nearby
    async def scan_for_BLE_devices(self, verbose=False):
        devices = await BleakScanner.discover()

        if verbose:
            for d in devices:
                print(d)
            print("=======================================")
            print("\n\n")

        # Update the view
        if not self.is_initial_scan:
            self.nearby_devices_view.delete(1, self.num_nearby_devices)
        else:
            self.is_initial_scan=False
        counter = 1

        for d in devices:
            self.nearby_devices_view.insert(counter, d)
            counter += 1

        self.num_nearby_devices = counter

        return devices
    

    # Connect to device and retreive info
    async def connect_to_selected_BLE_device(self, MAC_ADDR, verbose=False):
        if verbose:
            print(f"Instantiating connection to <{MAC_ADDR}>")

        # Store values of characteristics requested from GATT server
        characteristic_values = []

        # Connect to BLE device at MAC Address
        async with BleakClient(MAC_ADDR) as client:
            if verbose:
                print("\nServices:")
                for service in client.services:
                    print(service)

                print("\nCharacteristics:")
            
            for characteristic in client.services.characteristics:
                if verbose:
                    print(characteristic)

                char_s = client.services.get_characteristic(characteristic)
                if verbose:
                    print(f" --> {char_s}")

                try:
                    str_rep = await client.read_gatt_char(characteristic)
                    str_rep = str_rep.decode('utf-8')
                    if verbose:
                        print(f" --> {str_rep}")
                    characteristic_val = char_s + " : " + str_rep
                    characteristic_values.append(characteristic_val)
                except:
                    pass
                
            if verbose:
                print("\nDescriptors:")
                for descriptor in client.services.descriptors:
                    print(descriptor)

                    desc_str = client.services.get_descriptor(descriptor)
                    print(f" --> {desc_str}")
                    
                    try:
                        str_rep = await client.services.read_gatt_descriptor(descriptor)
                        str_rep = str_rep.decode('utf-8')
                        print(f" --> {str_rep}")
                    except:
                        pass
                

            # Populate device info dictionary
            self.active_BLE_client_info["MAC"] = MAC_ADDR
            self.active_BLE_client_info["Services"] = client.services
            self.active_BLE_client_info["Characteristics"] = client.services.characteristics
            self.active_BLE_client_info["Descriptors"] = client.services.descriptors
            self.active_BLE_client_info["Characteristics_Values"] = characteristic_values

        if verbose:
            print(f"\n\nTerminating connection to <{MAC_ADDR}>")


# Render GUI to screen   
root = Tk()
app = Window(root)
root.wm_title("Bluetooth Scanner")
root.geometry("500x350")
root.mainloop()
