import os
import sys
import csv
from datetime import datetime, timedelta

KAKAOTALK_CHAT_FILE_DATE_FORMAT = "%Y-%m-%d-%H-%M-%S"
KAKAOTALK_CHAT_FILE_PREFIX = "KakaoTalk_Chat"
KAKAOTALK_CHAT_MESSAGE_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
KAKAOTALK_ANALYZER_DATE_FORMAT = "%Y-%m-%d"


class KakaoAnalyzer:
    def __init__(self, talk_path: str, start_date: str, end_date: str):
        self.path = talk_path
        self.start = datetime.strptime(start_date, KAKAOTALK_ANALYZER_DATE_FORMAT)
        self.end = datetime.strptime(end_date, KAKAOTALK_ANALYZER_DATE_FORMAT) + timedelta(days=1)

    def run(self, save_dir: str):
        latest_chat = self._find_latest_chat()
        if latest_chat is None:
            print("There are no saved kakaotalk chat files.")
            return

        result = self._analysis(latest_chat, save_dir)
        if result is None:
            print("KakaoTalk analysis failed.")
            return

        print("KakaoTalk analysis success.")

    def _find_latest_chat(self) -> str:
        result = None
        latest_time_mills = None

        for file in os.listdir(self.path):
            if not file.startswith(KAKAOTALK_CHAT_FILE_PREFIX):
                continue

            date = file.split("_")[-1].replace(".csv", "")
            time_mills = datetime.strptime(date, KAKAOTALK_CHAT_FILE_DATE_FORMAT).timestamp()
            if result is None:
                result = file
                latest_time_mills = time_mills
            else:
                if latest_time_mills < time_mills:
                    result = file
                    latest_time_mills = time_mills

        return result

    def _read_talk(self, chat_file: str) -> [[str]]:
        talk = []

        with open("{}/{}".format(self.path.rstrip("/"), chat_file), 'r', encoding='utf-8') as f:
            rows = csv.reader(f)
            for row in rows:
                talk.append(row)

        return talk[1:]

    def _analysis(self, chat_file: str, save_dir: str) -> bool:
        talks = self._read_talk(chat_file)
        talk_dict = self._create_msg_dict(talks)
        try:
            self._save_result(talk_dict, save_dir)
            return True
        except IOError:
            return False

    def _create_msg_dict(self, talks: [[str]]):
        talk_dict = {}

        for talk in talks:
            date, name, msg = talk
            if not self._is_in_date(date):
                continue

            if name in talk_dict:
                talk_dict[name] += 1
            else:
                talk_dict[name] = 1

        return talk_dict

    def _save_result(self, talks: dict[str, int], save_dir: str) -> str:
        sorted_result = sorted(talks.items(), key=lambda item: item[1], reverse=True)
        save_time = datetime.now().strftime(KAKAOTALK_CHAT_FILE_DATE_FORMAT)
        save_file_name = "{}.txt".format(save_time)
        save_file_path = "{}/{}".format(save_dir.rstrip("/"), save_file_name)

        with open(save_file_path, 'w', encoding='utf-8') as f:
            for result in sorted_result:
                f.write("{} : {}회\n".format(result[0], str(result[1])))

        print("Create KakaoTalk analysis file. :: {}".format(save_file_path))
        return save_file_path

    def _is_in_date(self, msg_date: str) -> bool:
        msg_date_time = datetime.strptime(msg_date, KAKAOTALK_CHAT_MESSAGE_DATE_FORMAT)
        return self.start <= msg_date_time <= self.end


if __name__ == "__main__":
    args = sys.argv
    try:
        talk_path = args[1]
        start_date = args[2]
        end_date = args[3]
        save_dir = args[4]
        KakaoAnalyzer(talk_path, start_date, end_date).run(save_dir)
    except IndexError as e:
        print("Invalid arguments")

    except Exception as e:
        print("Process error {}".format(e))
