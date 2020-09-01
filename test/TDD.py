import unittest
from main import *


class Folder_sell_testcase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # TO-FIX descomentar el input en path para produccion.
        path = 'C:/Users/Tato/PycharmProjects/autoSell_Images/falsaRutatest/_x_Vender' # input('where is the sell folder? \n') or 'C:\TRABAJOS\Venta_stockfootage\_x_Vender'
        self.folder = Sell_folder(path)
        self.folder_items_list = self.folder.get_items_list()

    # buscar los archivos de la carpeta de salida llamada  "para vender"
    def test_looking_files_in_sell_folder(self):
        have_files_in_sellfolder = True if len(self.folder_items_list) > 0 else False
        self.assertEqual(have_files_in_sellfolder, True, msg="0 files were fund in sell folder")

    # ver si los archivos en la carpeta son validos para subir.
    def test_check_valid_videos_filetypes(self):
        # print(f'      ------  items in get items type: {self.folder.get_items_type()}\n')
        files_to_check = [ 'falsovideo.mov', 'video.avi', 'video.mp4']
        self.assertEqual(self.folder.check_acepted_filestype(files_to_check), True, msg='all the files in the folder are valid filetypes')
    def test_check_valid_videos_filetypes(self):
        # print(f'      ------  items in get items type: {self.folder.get_items_type()}\n')
        files_to_check = [ 'texto.txt', 'video.mpeg', 'video.mp4']
        self.assertEqual(self.folder.check_acepted_filestype(files_to_check), False, msg='Not all the files in the folder are valid filetypes')

    def test_files_classificator(self):
        files_to_check = [ 'falsovideo.mov', 'video.avi', 'video.h264', 'video.mpeg', 'texto.tx']
        check_valids = self.folder.files_types_clasificator(files_to_check)
        # print(f'\n--- Video dict is: {check_valids}')
        # print(check_valids[0])
        self.assertTrue(check_valids[0]) # dict of videos has two.
        self.assertIsNotNone(check_valids[4] , msg='the files on the list are not valid types') # dict of others has one item.

class testing_Sites_to_sell(unittest.TestCase):
    def setUp(self):
        site = "localFTP_for_test" #  "pond5"
        self.sites_sell = Sell_sites(site)

    #  entrar a sitios de ventas y sus datos de usuario
    def test_sell_sites_login_and_close(self):
        self.assertIn('220', self.sites_sell.login_ftp(), msg="Bad news, The FTP conection has not be success")
        self.assertIn('221', self.sites_sell.close_ftp())

    def test_sell_sites_upload_something_on_ftp(self):
        # probe if a file is uploaded confirmation.
        # use an dummy file to upload and delete after.
        file_for_upload = r"C:\Users\Tato\PycharmProjects\autoSell_Images\test\jpg_test_file.jpg"
        # print(file_for_upload.rsplit('\\')[1])
        filename = os.path.split(file_for_upload)[1].rsplit("/")[0]
        # open and login to ftp
        self.sites_sell.login_ftp()
        self.assertIn('226 Transfer complete.', self.sites_sell.upload_file_ftp(file_for_upload))
        self.sites_sell.ftp.delete(filename)
        # don't forget close ftp and say goodbye!
        self.sites_sell.close_ftp()

    def test_close_ftp(self):
        # open and login to ftp
        self.sites_sell.login_ftp()
        self.assertIn('221', self.sites_sell.close_ftp())

class Sheet_testing(unittest.TestCase):
    def setUp(self):
        self.sheet = "Copia_para_test_Subidas"
        self.sheet_id =  "1B2u8ahbrHLsARSwDU3DC3nik_rrnlO5K1nsBFx2HZ3o"

    def test_list_rows(self):
        self.ctrlsheet = Control_sheet(self.sheet, self.sheet_id )
        self.assertIsNotNone(self.ctrlsheet.list_rows('C4:E'))


    @classmethod
    def tearDownClass(cls):
        # A class method called after tests in an individual class have run.tearDownClass is called with the class as the only argument and must be decorated as a classmethod():
        # TO-DO ver en que class iba este metodo y que tiene que hacer.
        pass


if __name__ == '__main__':
    unittest.main()
