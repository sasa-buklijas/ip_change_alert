import urllib.request
from pathlib import Path
import json
import time
import socket

class IPChange:
    """   
    # status
    # last_ip
        # first seen
        # last check
    # previous_ip
        # first seen
        # last check
    """

    def __init__(self,):
        """Make data file, if it does not exist
        """

        # get full directory path to current file
        current_file_directory = Path(__file__).resolve().parent
        self._data_file_path = current_file_directory / "data.json"

        # make file if it does not exist
        if not self._data_file_path.exists():
            self._data_file_path.touch()    


    def check_external_ip(self):
        # get external ip
        request_time = time.time()
        print(f'Request sent to URL {request_time}')
        try:
            response = urllib.request.urlopen('https://api.ipify.org/', timeout=10)
        except urllib.error.URLError as e:
            if isinstance(e.reason, socket.timeout):
                print(f'Timed out after {time.time()-request_time:.2f} seconds.')
            else:
                print('An error occurred:', e)
            exit()
        print(f'Response took {time.time() - request_time:.2f} seconds')
        current_ip = response.read().decode()

        # get content of data from disk
        no_data = False
        if self._data_file_path.exists(): 
            with open(self._data_file_path) as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {}
                    no_data = True
        else:
            no_data = True
        print(f'Content of file {data=}')

        if no_data:
            data['status'] = 'first_run'
            data['last_ip'] = current_ip
            data['li_first_seen'] = request_time
            data['li_last_check'] = request_time
        else:
            if current_ip != data['last_ip']:
                print("novi IP")
                data['status'] = 'alert'
                data['previous_ip'] = data['last_ip']
                data['last_ip'] = current_ip
                data['pi_first_seen'] = data['li_first_seen']
                data['pi_last_check'] = data['li_last_check']
                data['li_first_seen'] = request_time
                data['li_last_check'] = request_time
            else:
                data['status'] = 'same'
                data['li_last_check'] = request_time

        # save data
        with open(self._data_file_path, 'w') as file:
            json.dump(data, file)

        # return data
        return data


def main():
    print('INIT') 
    ip = IPChange()
    data = ip.check_external_ip()
    print(data)

    if data['status'] == 'alert':
        msg = f"New IP {data['last_ip']} old IP was {data['previous_ip']}"
        print(msg)
        
        # For notification
        import tkinter as tk

        def close_window():
            root.destroy()

        root = tk.Tk()
        root.title('External IP changed !!!')
        root.geometry('300x100')

        label = tk.Label(root, text=msg, font=('Arial', 18))
        label.pack(pady=20)

        close_button = tk.Button(root, text="Close", command=close_window)
        close_button.pack()

        root.mainloop()


if __name__ == '__main__':
    main()