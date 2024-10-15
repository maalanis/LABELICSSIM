import logging
from datetime import datetime


from ics_sim.Device import HMI
from Configs import TAG, Controllers

logging.basicConfig(level=logging.DEBUG,
                    filename='app.log',  # Specify your log file's path here
                    filemode='a',  # 'w' will overwrite the log file each run; 'a' will append to the end of the log file
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class HMI1(HMI):
    def __init__(self):
        logging.debug(f"Entered _init_ on file hmi1")
        super().__init__('HMI1', TAG.TAG_LIST, Controllers.PLCs, 500)
        self._rows = {tag: {'tag': tag, 'msg1': '', 'msg2': ''} for tag in TAG.TAG_LIST.keys()}
        self._border = '-' * 70  # Example border length

    def _display(self):
        # Build and display the status table
        self.__show_table()

    def _operate(self):
        # Periodically update the messages displayed on the HMI
        self.__update_messages()

    def __update_messages(self):
        # Update the displayed information based on the current state of tags
        for tag_name in self.tags:
            try:
                tag_value = self._receive(tag_name)
                formatted_value = self.__format_tag_value(tag_name, tag_value)
                self._rows[tag_name] = formatted_value
                print(f"Tag Processed: {tag_name}, Value: {formatted_value}")  # Log successful processing
            except Exception as e:
                print(f"Error processing tag {tag_name}: {str(e)}")  # Log any errors during processing
                break  # Exit the loop to avoid further errors


    def __format_tag_value(self, tag_name, value):
        # Return formatted string based on the tag value
        if value is None:
            return "N/A"
        if isinstance(value, bool):
            return "ON" if value else "OFF"
        return str(value)

    def __show_table(self):
        # Show updated table in the HMI
        result = self._border + "\n"
        for tag_name, value in self._rows.items():
            result += f"| {tag_name}: {value}\n"
        result += self._border
        self.report(result)

if __name__ == '__main__':
    hmi1 = HMI1()
    hmi1.start()
