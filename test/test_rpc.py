import json
import unittest
from unittest.mock import MagicMock, patch
import rpc
import setting
import logging

class RpcTest(unittest.TestCase):
    def test_sessionID(self):
        mySetting = setting.Setting()
        # 더미 호스트
        mySetting.json["transmission"]["host"] = "555.168.0.1"
        sessionId = rpc.getSessionIdTransRpc(mySetting.getRpcUrl())
        self.assertIsNone(sessionId)

    @patch('rpc.requests')
    def test_sessionIDOfConfigFile(self, mock_requests):
        sessionId = "pI8na8XboVoe04bDOo1F0bVE5t89al766MJd3eWXa59kLYKp"
        # mock the response
        mock_response = MagicMock()
        mock_response.status_code = 409
        mock_response.text = f"<code>X-Transmission-Session-Id: {sessionId}</code>"

        # specify the return value of the get() method
        mock_requests.get.return_value = mock_response

        mySetting = setting.Setting()
        result = rpc.getSessionIdTransRpc(mySetting.getRpcUrl())
        logging.debug(f'session id: {result}')
        self.assertEqual(sessionId, result)

    @patch('rpc.requests')
    def test_패스워드가_다르면(self, mock_requests):
        # mock the response
        mock_response = MagicMock()
        # Unauthorized
        mock_response.status_code = 401
        mock_response.text = ""

        # specify the return value of the get() method
        mock_requests.get.return_value = mock_response

        mySetting = setting.Setting()
        mySetting.transPass = "5555"
        sessionId = rpc.getSessionIdTransRpc(mySetting.getRpcUrl())
        self.assertIsNone(sessionId)
    
    def create_patch(self, name):
         patcher = patch(name)
         thing = patcher.start()
         self.addCleanup(patcher.stop)
         return thing
    
    def test_rpc_다운로드_경로를_가져올수_있나(self):
        mock_sessionId = self.create_patch('rpc.getSessionIdTransRpc')
        mock_sessionId.return_value = "pI8na8XboVoe04bDOo1F0bVE5t89al766MJd3eWXa59kLYKp"

        mock_rpc = self.create_patch('rpc.rpc')
        download_dir = "/downloads_test"
        mock_rpc.return_value = {
            "arguments":{
			    "download-dir": download_dir
            }
        }

        mySetting = setting.Setting()
        dir = rpc.getDownloadDir(mySetting.getRpcUrl())
        logging.debug(f'download dir: {dir}')
        self.assertEqual(download_dir, dir)

    def test_addMagnet(self):
        mock_sessionId = self.create_patch('rpc.getSessionIdTransRpc')
        mock_sessionId.return_value = "pI8na8XboVoe04bDOo1F0bVE5t89al766MJd3eWXa59kLYKp"
        mock_requestPost = self.create_patch('requests.post')
        mockResponse = MagicMock()
        mock_requestPost.return_value = mockResponse
        mockResponse.status_code = 200
        mockResponse.json.return_value = {"result":"success"}

        mySetting = setting.Setting()
        mySetting.transPass = "testPassword"
        # 목업
        rpc.addMagnet("magnet:?xt=urn:btih:65f8977142095868204447f7b16430c750bfaced", "", mySetting.getRpcUrl())


if __name__ == '__main__':  
    unittest.main()