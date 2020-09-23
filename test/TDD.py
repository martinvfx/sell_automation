import unittest
from unittest.mock import patch
from main import *

## My configs
sheet_name = "Copia_para_test_Subidas"
sheet_id = "1B2u8ahbrHLsARSwDU3DC3nik_rrnlO5K1nsBFx2HZ3o"

class Folder_sell_testcase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # TO-FIX descomentar el input en path para produccion.
        self.path = r'C:/Users/Tato/PycharmProjects/autoSell_Images/falsaRutatest/_x_Vender' # input('where is the sell folder? \n') or r'C:\TRABAJOS\Venta_stockfootage\_x_Vender'
        self.folder = Sell_folder(self.path)
        self.folder_items_list = self.folder.get_items_list()

    def test_looking_files_in_sell_folder(self):
        # busca los archivos de la carpeta de salida llamada  "para vender"
        files_in_folder = self.folder_items_list
        print("\n".join(files_in_folder), sep="\n")
        self.assertGreaterEqual(len(files_in_folder), 1, msg="0 files were fund in sell folder")

    def test_check_valid_videos_filetypes(self):
        # ver si los archivos en la carpeta son validos para subir.
        # print(f'      ------  items in get items type: {self.folder.get_items_type()}\n')
        files_to_check = [ 'falsovideo.mov', 'video.avi', 'video.mp4']
        self.assertEqual(self.folder.check_acepted_filestype(files_to_check), True, msg='all the files in the folder are valid filetypes')
        files_to_check = [ 'texto.txt', 'video.mpeg', 'video.mp4']
        self.assertEqual(self.folder.check_acepted_filestype(files_to_check), False, msg='Not all the files in the folder are valid filetypes')

    def test_type_of_file(self):
        filename = 'video.mp4'
        returned = f'\t tested: {filename} is a valid {self.folder.type_file(filename)} type'
        print(returned)
        self.assertIn('video', returned, msg='that file are not a video file type')

    def test_files_classificator(self):
        files_to_check = [ 'falsovideo.mov', 'video.avi', 'video.h264', 'video.mpeg', 'texto.tx']
        check_valids = self.folder.files_types_clasificator(files_to_check)
        print(f'\n--- dict is: {check_valids}')
        print(f"only these files are valid videos: {check_valids[0]}")
        self.assertTrue(check_valids[0]) # dict of videos has two.
        self.assertIsNotNone(check_valids[4] , msg='the files on the list are not valid types') # dict of others has one item.

    def test_in_collection_subfolder(self):
        ## find collections: they are sub folders with more than 2 files located into 4K, HD, 3D main folders. Photos are not taken as possible collection type.
        folder_collection = self.folder.in_collection_subfolder()
        print("collections are: \n"+"\n".join(folder_collection))
        self.assertGreaterEqual(len(folder_collection), 1)


class testing_Sites_to_sell(unittest.TestCase):
    ## test for class Upload_to_sites()
    def setUp(self):
        site = "localFTP_for_test" #  "pond5"
        self.sites_sell = Upload_to_sites(site)

    def test_sell_sites_login_and_close(self):
        #  entrar a sitios de ventas con sus datos de usuario
        self.assertIn('220', self.sites_sell.login_ftp(), msg="Bad news, The FTP connection has not be success")
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

    def tearDown(self):
        self.sites_sell.close_ftp()

class Sheet_testing(Folder_sell_testcase):
    ## inherit testcase from Folder_sell_testcase Class.
    def setUp(self):
        super().setUpClass() ## supper for inherit folder path on this class.
        self.sheet_name = sheet_name
        self.sheet_id =  sheet_id

    def test_list_values_on_range(self):
        self.ctrlsheet = Control_sheet(self.sheet_id, self.sheet_name)
        values = self.ctrlsheet.list_values_on_range('C4:E')
        print(values)
        self.assertIsNotNone(values)

    # comprobar en la planilla que el archivo a subir no se haya subido ya manualmente.
    def test_find_in_sheet(self):
        self.ctrlsheet = Control_sheet(self.sheet_id, self.sheet_name)
        file_name = "vaca negra agua"
        confirmation = self.ctrlsheet.check_registred_file(file_name)
        print(f'{confirmation}: the file {file_name} is{" not" if confirmation==False else ""} registred in the sheet')
        self.assertTrue(confirmation)

    def test_record_filename(self):
        # if the file to sell doesn't exist on the sheet: record it.
        # print(str(os.path.normpath(self.path)))
        self.ctrlsheet = Control_sheet(self.sheet_id, self.sheet_name)
        # file_name = "_falsovideo_col1.mov" #  "filename_de_test.mov"
        # returned_action = self.ctrlsheet.record_filename(file_name, self.path)
        file_list = ['_falsovideo_col1.mov', '_falsovideo_col2.mov', "filename_de_test.mov"]
        for f in file_list:
            returned_action = self.ctrlsheet.record_filename(f, self.path)
            print(returned_action)
            self.assertIn(f, returned_action)
        # self.assertIn(file_name, returned_action)

    @classmethod
    def tearDownClass(cls):
        # A class method called after tests in an individual class have run.tearDownClass is called with the class as the only argument and must be decorated as a classmethod():
        # TO-DO ver en que class iba este metodo y que tiene que hacer.
        pass

class Sheet_test_with_mock(unittest.TestCase):
    def setUp(self):
        self.sheet_name = sheet_name
        self.sheet_id =  sheet_id
        self.ctrlsheet = Control_sheet(self.sheet_id, self.sheet_name)

    @patch('builtins.input', return_value= "1")
    def test_select_what_sites_ALL_sites(self, input):
        # TO-DO: La funcion debe fijarse que sitios tengo anotados en planilla, comprobar en el json, y preguntarme si elegir todos o quitar alguno.
        # All sites was selected for upload.
        print("\n>>> Testing option 1: All sites. \n")
        selected_sites = self.ctrlsheet.select_what_sites()
        self.assertIn('adobe Stock', selected_sites.values() )

    @patch('builtins.input', side_effect=["2", "0"])
    def test_select_what_sites_deselecting_one_site(self, input):
        # Pregunta a que sitios subir y eligue descartar el primer sitio ( indice 0 de la lista/diccionario).
        # La funcion debe fijarse que sitios tengo anotados en planilla, comprobar en el json, y preguntarme si elegir todos o quitar alguno.
        print("\n>>> Testing option 2: Deselect first site. \n")
        selected_sites = self.ctrlsheet.select_what_sites()
        self.assertNotIn('adobe Stock', selected_sites.values() )

    @patch('builtins.input', return_value= "3")
    def test_select_what_sites_defautl_option(self, input):
        # Pregunta a que sitios subir y eligue descartar el primer sitio ( indice 0 de la lista/diccionario).
        # La funcion debe fijarse que sitios tengo anotados en planilla, comprobar en el json, y preguntarme si elegir todos o quitar alguno.
        print("\n>>> Testing option 3: Use last time option ( saved ) . \n")
        selected_sites = self.ctrlsheet.select_what_sites()
        self.assertIn('Shutterstock', selected_sites[0].values() )

    def tearDown(self):
        unittest.mock.patch.stopall()



if __name__ == '__main__':
    unittest.main()
