import shutil, datetime, re
from pandas import DataFrame as df
from selenium import webdriver
import logging
import os, sys, json, ftplib, gspread
import os.path
import ffmpeg
import tempfile


logging.basicConfig(level=logging.DEBUG)

def temp_folder():
    # make a temp folder
    new_temp_folder = os.path.join(tempfile.gettempdir(), "autoSellimg_temp")
    if not os.path.exists(os.path.join(tempfile.gettempdir(), "autoSellimg_temp")):
        try:
            logging.info('\n-- temp folder will be created -- \n')
            os.mkdir(new_temp_folder)
            logging.info(f'System temp dir is {tempfile.gettempdir()}, and the new temp dir is on : {new_temp_folder}')
        except:
            logging.warning("\n!! Temp file can't be created! !! ")
    # shutil.rmtree(new_temp_folder)
    return new_temp_folder


acepted_video_filetypes = [ type.lower() for type in ['mov', 'mp4', 'mpg', 'avi']]
acepted_video_codec = [ type.lower() for type in [ 'ProRes', 'H.264', 'MPEG 2', 'MPEG 4', 'Motion', 'JPEG',  'PNG']] # 'MJPEG',
acepted_photos_filetypes =  [ type.lower() for type in ['jpg', 'PNG', 'tiff' ]]
acepted_illustrations_filetypes =  [ type.lower() for type in['AI', 'EPS', 'SVG' ]]
acepted_3D_filetypes = [ type.lower() for type in ['MA', 'MB', '3DS', 'MAX', 'C4D', 'BLEND' , 'XSI', 'LWO', 'OBJ', 'FBX', 'DAE']]
list_of_acepted_filetypes = acepted_video_filetypes + acepted_photos_filetypes + acepted_illustrations_filetypes + acepted_3D_filetypes

config_path = os.path.normpath(r"C:\Users\Tato\PycharmProjects\autoSell_Images\config")


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
    #     # self.sellfolder = str(os.path.normpath(input('where is the sell folder? \n') or r'C:\TRABAJOS\Venta_stockfootage\_x_Vender'))
        self.sellfolder = str(os.path.normpath(sellfolder_path))

    def get_items_list(self):
        ## Find the files in the output folder  "para vender" and in the nested subfolders.
        # self.sellfolder = str(os.path.normpath(input('where is the sell folder? \n') or r'C:\TRABAJOS\Venta_stockfootage\_x_Vender'))
        # self.sellfolder = str(os.path.normpath(sellfolder_path))
        items_in_folders = []
        def recursive_scan_folders(folder):
            with os.scandir(folder) as folder:
                if folder is not None:
                    for content in folder:
                        if content.is_file():
                            items_in_folders.append(content.name)
                        elif content.is_dir():
                            # print(content.name)
                            yield from  recursive_scan_folders(content.path)
                else:
                    logging.info('No files or foldes in this path')

        for i in recursive_scan_folders(self.sellfolder):
            next(recursive_scan_folders(i.path))

        return items_in_folders

    def check_acepted_filestype(self, items_list):
        ## Check if all files in upload or sell folder are valid types.
        files_types_found = []
        logging.debug(items_list)
        for file in items_list:
            extension_file = os.path.split(file)[1].rsplit('.')[1].lower()
            # logging.debug(f' ==== extension files var {extension_file}')
            if extension_file not in files_types_found:
                files_types_found.append(extension_file)
        logging.debug(f' found this filetypes in sell folder:\n{files_types_found}')
        return all(i in list_of_acepted_filetypes for i in files_types_found)


    def type_file(self, filename):
        # identificar que tipo de archivo tengo ( si es foto, video, ilustracion )
        extension_file = os.path.split(filename)[1].rsplit('.')[1].lower()
        if extension_file in acepted_video_filetypes:
            # video_type[filename] = 'video'
            file_type = 'video'
        if extension_file in acepted_photos_filetypes:
            file_type = 'Foto'
        if extension_file in acepted_illustrations_filetypes:
            file_type = 'illustration'
        if extension_file in acepted_3D_filetypes:
            file_type = '3D'
        if extension_file not in list_of_acepted_filetypes:
            file_type = 'other'
        ## this return the type of file.
        return file_type

    def files_types_clasificator(self, file_list):
        # clasificar por tipo de archivo para marcar al subir.
        video_type = {}
        photo_type = {}
        illustration_type = {}
        treeD_type = {}
        other_type = {}
        for file in file_list:
            extension_file = os.path.split(file)[1].rsplit('.')[1].lower()
            if self.type_file(file) == 'video':
                video_type[file] = 'video'
            if self.type_file(file) == 'Foto':
                photo_type[file] = 'Foto'
            if self.type_file(file) == 'illustration':
                illustration_type[file] = 'illustration'
            if self.type_file(file) == '3D':
                treeD_type[file] = '3D'
            if self.type_file(file) == 'other':
                other_type[file] = 'other'
            ## this return dict of every type.
        return video_type, photo_type, illustration_type, treeD_type, other_type

    def in_collection_subfolder(self):
        ## find collections: they are sub folders with more than 2 files located into 4K, HD, 3D main folders.
        # TO-DO Photos must be taken as possible collection type.
        container_collections = ['Foto', "3D", "4K", "HD"]
        collections = {}
        for category in container_collections:
            with os.scandir(os.path.join(self.sellfolder, category)) as sellfolder_toplevel:
                for sub_folder in sellfolder_toplevel:
                    if sub_folder.is_dir() and len(os.listdir(sub_folder)) >= 2:
                        # print(type(sub_folder), sub_folder.name +"\t"+ category)
                        for file in os.scandir(sub_folder):
                            if file.is_file():
                                # print(f'file es {file.name} en coleccion {sub_folder.name}')
                                if sub_folder.name in collections:
                                    collections[sub_folder.name].append(file.name)
                                else:
                                    collections[sub_folder.name] = [file.name]
        return collections


class Upload_to_sites():
    # lista de sitios de ventas y sus datos
    def __init__(self, site):# , user, passw):
        self.site_name = site
        ## archivo externo con datos de usuario de todos los sitios.
        with  open(os.path.join(os.path.dirname(__file__), 'my_sites_info.json'),  'r') as siteskeys:
            siteskeys = json.load(siteskeys)[site]
            # logging.debug(siteskeys['site'])
            # logging.debug(siteskeys['user'])
            self.site_url = siteskeys['site']
            self.user = siteskeys['user']
            self.passw = siteskeys['passw']

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
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("google.auth.transport.requests").setLevel(logging.WARNING)

        current_path = os.path.normpath(os.path.dirname(__file__))
        self.credentials_file = os.path.normpath(os.path.join(os.path.dirname(__file__), 'config/credentials.json'))
        token_file = os.path.normpath( os.path.join(current_path, 'config/token.pickle'))

        # check if credentials file are in the right place.
        cred_in_appdata = os.path.normpath(os.path.join(os.getenv('APPDATA'), "gspread/credentials.json"))
        if not os.path.isfile(cred_in_appdata):
            try:
                promp_path = input() or "Put the full path to file: credentials.json"
                self.credentials_file = os.path.normpath(os.path.join(promp_path, "credentials.json"))
                shutil.move(self.credentials_file, cred_in_appdata)
                logging.info(f"I can't fund credentials file in %APPDATA/gspread/% folder\nCredentials was moved to: {cred_in_appdata}")
            except:
                logging.info(Exception)

        self.sheet_id = sheet_id ## 1B2u8ahbrHLsARSwDU3DC3nik_rrnlO5K1nsBFx2HZ3o
        self.sheet_name = sheet_name

        self.gs = gspread.oauth()
        self.sh = self.gs.open_by_key(self.sheet_id)
        self.worksheet = self.sh.worksheet(self.sheet_name)
        self.all_ws_data = self.worksheet.get_all_values()
        # self.ws_as_df = df( self.worksheet.get_all_records())

    def select_what_sites(self):
        # extraer lista sitios y preguntar a que sitios subir.
        # La funcion debe fijarse que sitios tengo anotados en planilla, comprobar en el json, y preguntarme si elegir todos o quitar alguno.
        # sites_on_sheet = self.worksheet.get_all_records()
        col_tipos = self.worksheet.find(r"video / foto / 3D ").col
        col_title = self.worksheet.find(r"Titulo").col
        # lista de columnas con sitios de venta.
        nl = '\n'
        head_sites = self.worksheet.get(f'{str(chr(65+col_tipos))+"1"}:{str(chr(64+col_title-1))+"1"}')[0]
        head_sites = [i.strip() for i in head_sites] ## for trim the white spaces around.
        head_sites = (dict(zip(range(0, len(head_sites)) ,head_sites)))
        print(f"sites to sell are: {nl} {head_sites}".replace(',', nl), sep=nl)
        def saved_opt(mode, sel={}):
            ## That's for save selections in a file and read them as default option, to avoid re-ask every time to use.
            if mode is "read":
                with open(os.path.join(config_path, 'preferences.json')) as pref_file:
                    data = json.load(pref_file)['last_selected_to_upload']
                    # logging.info((", ".join(l for l in data[0].values())))
                    return data
            elif mode is "write":
                save_selection = {'last_selected_to_upload': [sel]}
                rw = 'w'
                with open(os.path.join(config_path, 'preferences.json'), rw) as pref_file:
                    json.dump(save_selection, pref_file, indent=4)

        select_menu = {"1":"All registred sell sites", "2":"Deselect some to discard in the upload", "3":"Use last used selection  (default)"}
        ask = False
        try:
            while ask == False:
                ask_sites = input(f"{'---'*8}\nPlease select the sites to upload: \n{str(select_menu).replace(',', nl)}\n\npress '1' key: If you want to use all sell site.\npress '2' key: If you want to deselect any sell site."
                                  f"\npress ENTER: If you want to upload to last selected sell sites.\nYour chose? = ") or "3"
                if ask_sites == "1":
                    # TO-DO check if all sites in spreadsheet as registred in json config.
                    print(select_menu[ask_sites], nl)
                    print(f"\nYou chosed all of sites: {', '.join(str(x) for x in head_sites.values())} to upload the files.")
                    ask = True
                    return head_sites
                elif ask_sites == "2":
                    print(select_menu[ask_sites], nl)
                    print(f"sites to sell are: {nl} {', '.join(str(x) for x in head_sites.items())}".replace(',', nl), sep=nl)
                    deselection = [int(i) for i in input("NOT do upload to these sites numbers\n(enter one or more numbers separated by commas) \nDeselect: ").split(',')] or []
                    print(f"\nThese sites will be no taken in account for next upload: {', '.join(head_sites[n] for n  in deselection)}")
                    head_sites = {k:head_sites[k] for k in head_sites if k not in deselection}
                    print(f"\nYou chosed {', '.join(str(x) for x in head_sites.values())} to upload the files.")
                    saved_opt("write", sel=head_sites) # I save the selected sites in a file.
                    ask = True
                    return head_sites
                elif ask_sites == "3":
                    # Read the preference file to avoid ask for selected sites again.
                    last_time_selected = saved_opt("read")
                    print(select_menu[ask_sites], nl)
                    print(f"\nYou chosed {', '.join(str(x) for x in last_time_selected[0].values())} to upload the files.")
                    logging.info(f'{nl}los sitios guardados son : {nl}{last_time_selected}')
                    ask = True
                    return last_time_selected
                else:
                    clear = lambda : os.system('cls' if os.name=='nt' else 'clear')
                    clear()
                    print("\n" * 55, "\nSorry , I can't stand your choice.", "\n"*3)
                    ask = False
        except:
            logging.debug(Exception)



    def list_values_on_range(self, range):
        # values_list = worksheet.col_values(1)
        values_list = self.worksheet.get(range)
        # print(f' valores de col 1 =\n{values_list}')
        return values_list

    def check_registred_file(self, file_name):
        # comprobar en la planilla que el archivo a subir no se haya subido ya anteriormente o manualmente.
        rec_names = self.worksheet.col_values(ord("D")-64)
        ## I use pandas to check rows
        # logging.debug(df(rec_names, columns=['Names of registred uploads']).shift(1))             # TO-FIX no está listando hasta el ultimo nombre de la columna D
        if any(file_name in f for f in rec_names):
            return self.worksheet.find(re.compile(rf'{file_name}')).row  ## return position row
        else:
            return False

    def update_state(self, state, row_position, col_letter):
        ## https://www.rapidtables.com/web/color/RGB_Color.html
        if state == "subiendo" :
            color_state = {"red": 1, "green":  0.85, "blue": 0.4} # yellow "subiendo"
        if state == "pendiente" :
            color_state = {"red": 1.0, "green": 0.9, "blue": 0.40} # yellow "pendiente"
        if state == "revision" :
            color_state = {"red":  0.57, "green": 0.76, "blue": 0.49} # low-green "revision"
        if state == "OK" :
            color_state = {"red": 0.0, "green": 1, "blue": 0.0} # green "OK"
        if state == "rechazo" :
            color_state = {"red": 1, "green": 0.01, "blue": 1} # magenta "rechazo "

        self.worksheet.update(col_letter+str(row_position), state)
        self.worksheet.format(col_letter+str(row_position), {"backgroundColor": color_state})


    def record_filename(self, filename, sell_folder_path):
        # if the file to sell doesn't exist on the sheet: record it.
        self.sellfolder = str(os.path.normpath(sell_folder_path))
        check = self.check_registred_file(filename)
        # logging.debug(check)
        if check is False:
            last_row = len(self.worksheet.col_values(ord("D")-64))+1 # ord("D")-64 it's the numeric translation of "D" column
            collection = Sell_folder(sellfolder_path=sell_folder_path).in_collection_subfolder()
            ## I search for filename into collections.
            old_collection = {}
            new_collection = {}
            for coll_key, file in collection.items():
                # print(coll_key, file)
                if filename in str(file):
                    # TO-DO
                    ## tomar el nombre actual antes de agregarle nada.
                    ## insertarle el filename nuevo despues de los que existen.
                    ## reeemplazar variable filename_record.
                    old_collection.update({coll_key:[].append(filename)}) # TO-FIX no está sumando valores, los está pisando en cada iteracion .
                    print('\n'+f'-------... ------ {old_collection} it is in collection ')
                    # print(f'------------- {filename} it is in collection ')
                    ## I change the name to record.
                    filename_record = str(old_collection)
                    # filename_record = f'{coll_key}: ({filename})'
                    ## check filetype and write it in the 4th column.
                    try:
                        check_exist =  self.worksheet.find(re.compile(rf'{coll_key}'))
                    except:
                        check_exist = False

                    logging.debug(f'-.-.-.- {check_exist} antes de if ')

                    if check_exist:
                        # this_cell = self.worksheet.find(re.compile(rf'{coll_key}'))
                        # current_row = len(self.worksheet.col_values(ord("D")-64))+1 # ord("D")-64 it's the numeric translation of "D" column
                        print(f'-.-.-.- { check_exist.row}')
                        self.worksheet.update("D" + str(check_exist.row), str(old_collection))
                    else:
                        # self.worksheet.update("D" + str(last_row), filename)
                        pass

            # if filename not in collection.values():
            #     #     filename_record = filename
            #     ## check filetype and write it in the 4th column.
            #     logging.debug(f'*** { filename} not in collection *** ')
            #     self.worksheet.update("D" + str(last_row), filename)

            type_of_file = Sell_folder(sell_folder_path).type_file(filename)
            self.worksheet.update("E"+str(last_row), type_of_file)
            date = str(datetime.date.today()).replace('-', "/")
            self.worksheet.update("B"+str(last_row), date)
            # TO-DO: mandar a subir por FTP y marcar "subiendo" en todos los sitios.
            self.update_state( "subiendo", last_row, "F") # TO-FIX hardcode letter of col
            return f'{filename} will be included in the records of sheet'
        else:
            # logging.debug(f'\nthe file {filename} already exist in the sheet records at the row {check}')
            return  'the file already exist in the sheet records'


    def thumbnail_generation(self, input_file, sufix):

        ## take the original filename and make a picture thumbnail
        # logging.debug(f'__ the input file is {input_file}')
        sufixname = sufix or "_thumbn.jpg"
        out_thumbnail_name = os.path.normpath(f"{os.path.splitext(input_file)[0]}{sufixname}")
        ## check acepted graphic filetypes before start to do thumbnails.
        if str(os.path.splitext(input_file)[1]).lower().replace('.', '') in (acepted_video_filetypes + acepted_photos_filetypes):
            if  os.path.exists(out_thumbnail_name) is False and os.path.splitext(sufixname)[0] not in str(os.path.splitext(input_file)[0]):
                (
                    ffmpeg
                        .input(input_file ) # ss=1 TO-DO find the middle of the duration and use that to set "ss=time" only if it's a video file.
                        .filter('scale', 50, -1)
                        .output(out_thumbnail_name, vframes=1)
                        .run()
                )
        path_output_thumbnails = os.path.join(temp_folder(), os.path.basename(out_thumbnail_name))
        logging.debug(f'__ the output file will be in {path_output_thumbnails}')

        ## Move thumbnails to Temp directory
        shutil.move(out_thumbnail_name, path_output_thumbnails )

    def check_thumbnail_exist(self):
        pass


    # if __name__ == '__main__':
#     sheet_name = "Copia_para_test_Subidas"
#     sheet_id = "1B2u8ahbrHLsARSwDU3DC3nik_rrnlO5K1nsBFx2HZ3o"
#
#     print(Control_sheet(sheet_id, sheet_name).list_cols('C4:E'))

# shutil.rmtree(new_temp_folder)

