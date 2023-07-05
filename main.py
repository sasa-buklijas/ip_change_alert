import urllib.request
from pathlib import Path
import json
import time
import socket
from datetime import datetime, timedelta

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
        #except socket.timeout as e:
        except TimeoutError as e:
            print("The connection timed out.", e)
            exit()
        except Exception as e:
            # Handle the exception
            print("An error occurred:", e)
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
        #print(f'Content of file {data=}')

        if no_data:
            data['status'] = 'first_run'
            data['last_ip'] = current_ip
            data['li_first_seen'] = request_time
            data['li_last_check'] = request_time
        else:
            if current_ip != data['last_ip']:
                #print("novi IP")
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
    print('\nINIT') 
    ip = IPChange()
    data = ip.check_external_ip()
    #print(data)

    def hrd(utt: float) -> str:
        """To human readable date (%d/%m/%Y %H:%M:%S)
        utt is abbreviation for unix time stamp"""
        return datetime.fromtimestamp(utt).strftime('%d/%m/%Y %H:%M:%S')
    
    def diff(timestamp1, timestamp2):
        """Return difference between two unix time stamps in human readable form."""
        if timestamp1 > timestamp2:
            raise ValueError('timestamp1 cannot be larger than timestamp2.')

        # Calculate the time difference
        time_difference = abs(timestamp1 - timestamp2)
        time_delta = timedelta(seconds=time_difference)
        #print(f'{time_delta=}')

        # Format the time difference in a human-readable form
        days = time_delta.days
        hours, remainder = divmod(time_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Generate the human-readable time difference string
        return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"

    if data['status'] == 'alert':
        old_ip_first_seen = hrd(data['pi_first_seen'])
        old_ip_last_check = hrd(data['pi_last_check'])
        old_ip_duration = diff(data['pi_first_seen'], data['pi_last_check'])

        msg = \
        f"New IP  is: {data['last_ip']}\n" +\
        f"old IP was: {data['previous_ip']}\n" +\
        f"New IP first seen on {hrd(data['li_last_check'])}\n\n" +\
        f"old IP from {old_ip_first_seen} to {old_ip_last_check}\n" +\
        f"old IP was in use {old_ip_duration}.\n" +\
        "\n" +\
        "Time duration is calculated from last checked time,\n" +\
        "last checked time is not exact time when IP was changed,\n" +\
        "it happened sometime between last checked time an New IP first seen on."
        #print(msg)
        
        # For notification
        import tkinter as tk

        def close_window():
            root.destroy()

        root = tk.Tk()
        root.title('External IP changed !!!')
        root.geometry('700x300')
        root.resizable(False, False)

        label = tk.Label(root, text=msg, font=('Arial', 18), justify='left')
        label.pack(pady=20)

        close_button = tk.Button(root, text="Close", command=close_window)
        close_button.pack()

        root.mainloop()

        # add to log file
        with open('log_ip.txt', 'a+') as file:
            file.write(
        f"{data['previous_ip']} - from {old_ip_first_seen} to {old_ip_last_check}"+\
        f" - {old_ip_duration} - IP change first seen on {hrd(data['li_last_check'])}\n"
        )

if __name__ == '__main__':
    main()