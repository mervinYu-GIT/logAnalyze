import sys, os
sys.path.append(os.path.abspath("../modules"))
from datetime import datetime
import unittest
from navLog import NavLogFile
#---------------------------------------- Test ----------------------------------------#
class TestNavLog(unittest.TestCase):
    """ test class navLog """
    def setUp(self):
        test_file = "../../loganalysis/navigation-logs/navigation10.log"
        self.test_nav_log = NavLogFile(test_file)
        self.test_case_1 = "P12.R080.02 :Start marker for navigation route calculation"
        self.test_case_2 = "P12.R080.02,P12.R081.02 :End marker for navigation route calculation"
        self.test_result_1 = ["1.01.2000 12:04:07:396", "1.01.2000 12:04:07:638", "1.01.2000 12:04:29:286",
                    "1.01.2000 12:04:42:168", "1.01.2000 12:05:29:957", "1.01.2000 12:06:05:757",
                    "1.01.2000 12:07:42:771", "1.01.2000 12:08:12:428", "1.01.2000 12:08:29:815",
                    "1.01.2000 12:09:05:321", "1.01.2000 12:09:42:898", "1.01.2000 12:10:37:201",
                    "1.01.2000 12:11:17:357", "1.01.2000 12:11:46:162", "1.01.2000 12:13:11:671",
                    "1.01.2000 12:15:10:786", "1.01.2000 12:25:05:919", "1.01.2000 12:25:17:362",
                    "1.01.2000 12:25:17:916", "1.01.2000 12:26:20:843", "1.01.2000 12:26:33:944",
                    "1.01.2000 12:28:46:275", "1.01.2000 12:29:02:231", "1.01.2000 12:30:17:221",
                    "1.01.2000 12:30:39:238", "1.01.2000 12:31:29:217", "1.01.2000 12:31:48:495",
                    "1.01.2000 12:32:00:831", "1.01.2000 12:35:07:693", "1.01.2000 12:40:01:892",
                    "1.01.2000 12:44:08:520"]
        self.test_result_2 = ["1.01.2000 12:04:10:556", "1.01.2000 12:04:31:272", "1.01.2000 12:04:43:975",
                  "1.01.2000 12:05:31:834", "1.01.2000 12:06:07:557", "1.01.2000 12:07:45:031",
                  "1.01.2000 12:08:14:355","1.01.2000 12:08:32:588","1.01.2000 12:09:07:160",
                  "1.01.2000 12:09:44:983","1.01.2000 12:10:52:662","1.01.2000 12:11:29:062",
                  "1.01.2000 12:11:58:786","1.01.2000 12:13:29:231","1.01.2000 12:15:27:338",
                  "1.01.2000 12:25:07:829","1.01.2000 12:25:18:620","1.01.2000 12:26:27:366",
                  "1.01.2000 12:26:41:088", "1.01.2000 12:28:54:558", "1.01.2000 12:29:07:479",
                  "1.01.2000 12:35:12:277", "1.01.2000 12:40:05:734", "1.01.2000 12:44:13:311"]
        self.test_times1 = [1,3,6,9,12,14]
        self.test_times2 = [4,7,8,10,11,15]
        self.test_result = [3,4,6,7,9,10,14,15]


    def test_searchLogs(self):
        key = self.test_case_1
        item = 'Message'
        result = self.test_result_1
        times = []

        logs = self.test_nav_log.searchLogs(key, item)
        for log in logs:
            times.append(log[1])

        self.assertListEqual(times, result)


    def test_getLogsTime(self):
        results = []
        key = self.test_case_2
        logs = self.test_nav_log.searchLogs(key, "Message")
        times = self.test_nav_log.getLogsTime(logs)
        for mg in self.test_result_2:
            mg_time = datetime.strptime(mg, "%d.%m.%Y %H:%M:%S:%f")
            results.append(mg_time)

        self.assertListEqual(times, results)


    # def test_logTimeMatching(self):
    #     test_times1 = [1,3,6,9,12,14]
    #     test_times2 = [4,7,8,10,11,15]
    #     test_result = [3,4,6,7,9,10,14,15]

    #     result = self.test_nav_log.logTimeMatching(test_times1, test_times2)

    #     self.assertListEqual(test_result, result)

    
    def test_getDeltaTime(self):
        begin_times = self.test_times1
        end_times = self.test_times2
        dest_results = [1,1,1,1]

        results = self.test_nav_log.getDeltaTime(begin_times, end_times)

        self.assertLessEqual(dest_results, results)



unittest.main()