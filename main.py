from selenium import webdriver
import logging
import os, sys, json, ftplib

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

logging.basicConfig(level=logging.DEBUG)

acepted_video_filetypes = [ type.lower() for type in ['mov', 'mp4', 'mpg', 'avi']]
acepted_video_codec = [ type.lower() for type in [ 'ProRes', 'H.264', 'MPEG 2', 'MPEG 4', 'Motion', 'JPEG',  'PNG']] # 'MJPEG',
acepted_photos_filetypes =  [ type.lower() for type in ['jpg', 'PNG', 'tiff' ]]
acepted_illustrations_filetypes =  [ type.lower() for type in['AI', 'EPS', 'SVG' ]]
acepted_3D_filetypes = [ type.lower() for type in ['MA', 'MB', '3DS', 'MAX', 'C4D', 'BLEND' , 'XSI', 'LWO', 'OBJ', 'FBX', 'DAE']]
list_of_acepted_filetypes = acepted_video_filetypes + acepted_photos_filetypes + acepted_illustrations_filetypes + acepted_3D_filetypes


class Setup_driver():
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome('C:/Program Files (x86)/Google/chromedriver_selenium/chromedriver.exe', options=chrome_options)
        self.driver.get('http')
        self.driver.implicitly_wait(6)
        self.driver.quit()

class Sell_folder():
    def __init__(self, sellfolder_path):
        # self.sellfolder = input('where is the sell folder?') if "" else 'C:\TRABAJOS\Venta_stockfootage\_x_Vender'
        self.sellfolder = sellfolder_path

    ## buscar los archivos de la carpeta de salida  "para vender"
    def get_items_list(self):
        items_lists = []
        # List all files in a directory
        with os.scandir(self.sellfolder) as folder:
            if folder is not None:
                for file in folder:
                    if file.is_file():
                        items_lists.append(file.name)
                        # logging.info(items_lists)
            else:
                logging.info('No files in this folder')
        return items_lists

    ## Check if all files in upload or sell folder are valid types.
    def check_acepted_filestype(self, items_list):
        files_types_found = []
        logging.debug(items_list)
        for file in items_list:
            extension_file = os.path.split(file)[1].rsplit('.')[1].lower()
            # logging.debug(f' ==== extension files var {extension_file}')
            if extension_file not in files_types_found:
                files_types_found.append(extension_file)
        logging.debug(f' found this filetypes in sell folder:\n{files_types_found}')
        return all(i in list_of_acepted_filetypes for i in files_types_found)


    # identificar que tipo de archivo tengo ( si es foto, video, ilustracion )
    # clasificar por tipo de archivo para marcar al subir.
    def files_types_clasificator(self, file_list):
        # items_list = self.get_items_list()
        video_type = {}
        photo_type = {}
        illustration_type = {}
        treeD_type = {}
        other_type = {}
        for file in file_list:
            extension_file = os.path.split(file)[1].rsplit('.')[1].lower()
            if extension_file in acepted_video_filetypes:
                video_type[file] = 'video'
            if extension_file in acepted_photos_filetypes:
                photo_type[file] = 'Foto'
            if extension_file in acepted_illustrations_filetypes:
                illustration_type[file] = 'illustration'
            if extension_file in acepted_3D_filetypes:
                treeD_type[file] = '3D'
            if extension_file not in list_of_acepted_filetypes:
                other_type[file] = 'other'
            ## this return dict of every type.
        return video_type, photo_type, illustration_type, treeD_type, other_type

class Sell_sites():
    # TO-DO: armar la lista de sitios de ventas y sus datos de usuario
    def __init__(self, site):# , user, passw):
        ## archivo externo con datos de usuario de todos los sitios.
        with  open(os.path.join(os.path.dirname(__file__), 'my_sites_info.json'),  'r') as siteskeys:
            siteskeys = json.load(siteskeys)[site]
            # logging.debug(siteskeys['site'])
            # logging.debug(siteskeys['user'])
            self.site_url = siteskeys['site']
            self.user = siteskeys['user']
            self.passw = siteskeys['passw']


    # def sites_info_file(self, site_url):
    #     sites_dict = {'pond5': 'ftp.pond5.com'}
    #     ## archivo externo con datos de usuario de todos los sitios.
    #     with  open('my_sites_info.json',  'r') as siteskeys:
    #         # logging.debug(siteskeys.readlines())
    #         logging.debug(json.loads(siteskeys[site_url]))
    #         return json.loads(siteskeys[site_url])



    def login_ftp(self):
        logging.info(f"\nsigin into {self.site_url} with {self.user} username.") # just for test.

        # Connect
        self.ftp = ftplib.FTP(self.site_url)
        self.ftp.login(user=self.user, passwd=self.passw) # ("user", "passwd")
        # self.ftp = ftp
        # show success
        login_success = self.ftp.getwelcome() ## 220 is a welcome code.
        logging.info(login_success)

        connected = True

        # self.close_ftp() # dejar ésto solo para pruebas.

        # Is ftp still a valid obj?
        logging.debug(type(self.ftp))

        # Is ftp None?
        if self.ftp is None:
            logging.info("ftp is None.")
        else:
            logging.info("ftp is still assigned, but closed")

        # check if open
        try:
            self.ftp.voidcmd("NOOP")
        except AttributeError as e:
            errorInfo = str(e).split(None, 1)[0]
            logging.debug(errorInfo)
            connected = False

        if connected:
            logging.info("Connection is open.")
        else:
            logging.info("Connection already closed.")

        return login_success

    def upload_file_ftp(self, file):
        filename = os.path.split(file)[1].rsplit("/")[0]

        ## NLST retrieves a list of file names.
        try:
            ## codigo 226 indica que se transfirio correctamente.
            with open(file, "rb") as file:
                # use FTP's STOR command to upload the file
                sending = self.ftp.storbinary(f"STOR {filename}", file)
            logging.info(f'{filename} has ben uploaded successfully to the {self.site_url} ftp server.')
            return sending
        except:
            # *resp* '550-Access is denied --- es cuando el server no deja escribir.
            except_messagge = "Error:", sys.exc_info()[0]
            logging.info(f'{except_messagge} was the error')
            return except_messagge, Exception

    def close_ftp(self):
        # Close connection
        try:
            return self.ftp.quit()
        except:
            return self.ftp.close()


class Control_sheet():
    def __init__(self, sheet_id, sheet_name):
        self.sheet_id = sheet_id ## 1B2u8ahbrHLsARSwDU3DC3nik_rrnlO5K1nsBFx2HZ3o
        self.sheet_name = sheet_name

        current_path = os.path.normpath(os.path.dirname(__file__))
        credentials_file = os.path.normpath(os.path.join(os.path.dirname(__file__), 'config/credentials.json'))
        token_file =os.path.normpath( os.path.join(current_path, 'config/token.pickle'))
        print(token_file)
        # print(credentials_file)

        # If modifying these scopes, delete the file token.pickle.
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

        # The ID of spreadsheet.
        self.SPREADSHEET_ID = self.sheet_id

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)

    def list_rows(self, range):

        self.SHEET_NAME_RANGE = f'{self.sheet_name}!{range}'  # A2:E

        # Call the Sheets API
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.SPREADSHEET_ID,
                                    range=self.SHEET_NAME_RANGE).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
        else:
            print('archivo \t tipo  \t estado \n -----------------------')
            for col in values:
                # Print columns A and E, which correspond to indices 0 and 4.
                print(f'{col[0]} \t {col[1]}') # \t {col[2]}')


if __name__ == '__main__':
    sheet = "Copia_para_test_Subidas"
    sheet_id = "1B2u8ahbrHLsARSwDU3DC3nik_rrnlO5K1nsBFx2HZ3o"

    print(Control_sheet(sheet_id, sheet).list_rows('C4:E'))
