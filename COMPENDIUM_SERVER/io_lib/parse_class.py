import  re
import  os
import  logging
import  argparse
import  datetime
import  unicodedata
import  urllib2
#import  progressbar
import  io_debug, io_mysql
import zones_keywords as keys
from    bs4        import BeautifulSoup
#from skipfiles import skipBoletines
#===========================   PARSER CONFIG =======================
CLOUD_LOGGING = os.environ.get('ENABLE_CLOUD_LOGGING')

if CLOUD_LOGGING:
    # dont' user io_debug, use directly logging.debug for now.
    # https://cloud.google.com/appengine/docs/standard/python/logs/
    from google.appengine.api import mail

# DB_ENTRIES is the placeholder to fill a row in "resoluciones" mysql db table
# when scanning a new "Boletin", the table looks like follows:
#
# resoluciones (
# [0]  fecha_url,
# [1]  fecha_boletin,
# [2]  ciudad,
# [3]  juzgado,
# [4]  ramo,
# [5]  sala_secretaria,
# [6]  tipo,
# [7]  no_resolucion,
# [8]  no_expediente,
# [9]  contenido,
# [10]  firma);
#
DB_fecha_url      = 0
DB_fecha_boletin  = 1
DB_ciudad         = 2
DB_juzgado        = 3
DB_ramo           = 4
DB_ss             = 5
DB_tipo           = 6
DB_nr             = 7
DB_ne             = 8
DB_contenido      = 9
DB_firma          = 10
DB_TABLE_RESOLUCIONES_SIZE = 11

levelOptions      = [0] * 4

LVL_AUTO          = 0
LVL_RAMO          = 1
LVL_SS            = 2
LVL_TIPO          = 3
#AUTORIDAD
levelOptions[LVL_AUTO]  = ('Juzgado',
                           'H. Tribunal Superior De Justicia')
# RAMO
levelOptions[LVL_RAMO]  = ('Acuerdos En El Ramo',
                           'Seccion De Amparos Ramo',
                           'Sala Unitaria Especializada En Justicia Para Adolescentes',
                           'Acuerdos De Presidencia',
                           'Nuevo Sistema De Justicia Penal',
                           'Seccion Civil',
                           'Seccion Penal')
# SS
levelOptions[LVL_SS]    = ('Secretaria',
                           'Sala')

# TIPO_RESOLUCION
levelOptions[LVL_TIPO]  = ('Acuerdos',
                           'Admisiones',
                           'Audiencias',
                           'Sentencias',
                           'Sentencia',
                           'Exhortos',
                           'Cuadernillo',
                           'Cuadernos De Amparo',
                           'Cuadernos De Antecedentes',
                           'Cuadernos De Cancelacion',
                           'Expedientes Bis',
                           'S/C',
                           'Requisitorias')

available_zones = ['Tijuana', 'Ensenada', 'Mexicali', 'Tecate', 'Mixtos', 'Baja California']
#===========================  PARSER CONFIG =======================

class Parser():
    # Make this true when you want to output a complete debug log, at least more informative.
    debug_all = False
    DB_ENTRIES        = []
    DB_ENTRIES_tmp    = [""] * DB_TABLE_RESOLUCIONES_SIZE
    io_print          = None
    io_mysql          = None
    io_email          = None
    io_debug          = None
    # === for parse_daily ====
    year         = 0
    month        = 0
    day          = 0
    END_OF_MONTH = 31
    LAST_MONTH   = 12
    december_vacations = False
    city = 'None'
    link = 'None'
    zone = 'None'
    # ==== done ===
    def __init__(self, io_print=False, io_log=None, printAll=False, buffPrints=False):
        # printAll means we want to turn on print's also from inside io_lib classes
        # maybe this will not be needed later, for now leaving the comment up in the air.
        self.cnt = 0
        if printAll:
            self.io_debug = io_debug.io_debug(io_print, io_log,buffPrints)
            self.io_mysql = io_mysql.io_mysql(io_print, io_log, io_print)
            #self.io_email = io_notify.io_notify(io_print,io_log,io_print)
        else:
            self.io_debug = io_debug.io_debug(False, io_log,buffPrints)
            self.io_mysql = io_mysql.io_mysql(False, io_log, io_print)
            #self.io_email = io_notify.io_notify(False,io_log,io_print)
        # To use self.io_print across class to print
        # Setup io_mysql and io_print if we are at cloud.
        if os.environ.get('ENABLE_CLOUD_LOGGING'):
            # dont' user io_debug, use directly logging.debug for now.
            # https://cloud.google.com/appengine/docs/standard/python/logs/
            self.io_print = logging.debug
        else:
            self.io_print = self.io_debug.io_print
        return

    def extractHTML(self, url):
        # extract date of boletin from url.
        f = open(url[45:] + 'l', 'w')
        boletin = urllib2.urlopen(url)
        boletinhtml = boletin.read()
        f.write(boletinhtml)
        f.close()

    def soupme(self, localfile = False, link = ''):
        try:
            if not localfile:
                html = urllib2.urlopen(link)
                # PJBC website is redirecting to home page rather than what was originally doing, replying with an 404 error.
                if html.geturl().find('boletinj') == -1:
                    self.io_print('\tNo boletin available for: ' + link)
                    raise Exception("NO_BOLETIN")
                soup = BeautifulSoup(html, 'html.parser')
            else:
                soup = BeautifulSoup(open(link), 'html.parser')
            return soup
        except Exception as e:
            # PENDING TO DIFFERENTIATE FROM AN INVALID LINK AND A SOUR ERROR
            #self.io_print(e)
            raise

    def parse_boletin(self, localfile = False, link = '', zone = 'all'):
        # link = 'http://www.pjbc.gob.mx/boletinj/2017/my_html/bc171030.htm'
        self.io_print('Scraping: ' + link)
        self.DB_ENTRIES[:] = []
        try:
            self.link = link
            soup = self.soupme(localfile, link)
        except Exception as e:
            self.io_print(e)
            return False
        try:
            if zone == 'all':
                if self.scanSoup(soup, 'Baja California'):
                    if self.scanSoup(soup, 'Mexicali'):
                        if self.scanSoup(soup, 'Tijuana'):
                            if self.scanSoup(soup, 'Ensenada'):
                                return True
                raise
            elif zone in available_zones:
                if zone == 'Mixtos':
                    self.scanSoup(soup, zone + '_cdmorelos')
#                     self.scanSoup(soup, zone + '_Rosarito')
#                     self.scanSoup(soup, zone + '_SanFelipe')
#                     self.scanSoup(soup, zone + '_SanQuintin')
#                     self.scanSoup(soup, zone + '_GuadalupeV')
                    return True
                self.scanSoup(soup, zone)
                return True
            else:
                self.io_print('[x] Unknown zone...')
        except:
            self.io_print('[x] Error parsing link for ' + zone + ' : ' + link)
            return False
        return False

    # ========== SCAN SOUP ==============
    # Main method to extract files from a 'boletin'.
    # The algorithm looks for data in the format shown above, 
    # A file will look in our data base like the following:
    #
    # | a* | a* | a* | a* | a* | b | c | x | y | z | s |
    # (a* this means each field get's parsed from element 'a')
    # a -> zone jury (like 'juzgado primero civil tijuana, a 10 de Enero del 2008.')
    # b -> room (like 'primera secretaria')
    # c -> type of file (like 'acuerdos')
    # x ->
    # y ->
    # z ->
    # | a |
    # | b |
    # | c |
    # | x - y - z |
    # | x - y - z |
    #       .
    #       .
    #       n
    # | a | or | b | or | c |
    #
    # UNDER CONSTRUCTION
    # 
    def scanSoup(self, soup, zone):
        self.zone = zone
        # clear 'resoluciones' list
        self.DB_ENTRIES_tmp[:] = [''] * DB_TABLE_RESOLUCIONES_SIZE
        self.io_print('\n[Executing scanHTML for ' + zone + ']')
        # get starting point
        self.getStarting(soup)

        doneExtracting = False
        # Start extracting
        while not doneExtracting:
            # =======CHECK TERMINATOR (EXIT CONDITION)=======
            cleanText = self.splitandmergeText(self.next_element.text)
            if self.idx_level == LVL_AUTO and \
                    (cleanText.find(zone) == -1 or \
                     cleanText.find('Paz Civil') > -1 or \
                     cleanText.find('E D I C T O') > -1):
                self.io_print('[The End - found valid terminator]')
                doneExtracting = True
                break
            #==============================
            # PENDING
            # get sign
            self.DB_ENTRIES_tmp[DB_firma] = 'TBD'
            #self.io_print('--> Scanning idx_level: ' + str(self.idx_level))
            # =======SCAN CONTENTS=======
            if not self.scanContent():
                return False
            # =======MOVE POSITION=======
            self.moveChips()
        return True
    # ========== [end] scanSoup ==============

    def getStarting(self, soup):
        firstElement = self.firstElement(soup)
        if firstElement is None:
            for each in skipBoletines:
                if self.link == each[1] and self.zone == each [0]:
                    self.io_print("Skip this link. Nothing to parse.")
                    return False
            self.io_print('[x] abort problems finding first element or no files for this zone today.')
            self.io_print(self.link)
            # [kill condition] use raise?
            return False
        # Now that we know we are at the starting point, we can store
        # some default information for this case in DB_ENTRIES
        #
        # Saving "ciudad" in DB[1] --> ciudad
        if 'Mixtos' in self.zone:
            self.DB_ENTRIES_tmp[DB_ciudad] = self.city
        else:
            self.DB_ENTRIES_tmp[DB_ciudad] = self.zone
        if self.zone == 'Baja California':
            # Get date
            tmpzone = self.zone 
            self.zone = 'Tijuana'
            tmp = self.firstElement(soup)
            self.zone = tmpzone
            dateElement = self.getDate(tmp + tmp.find_next('span').text)
        elif self.zone == 'Tijuana':
            # Get date, firstElement should contain the date
            dateElement = self.getDate(firstElement + firstElement.find_next('span').text)
        else:
            # Get date, firstElement should contain the date
            dateElement = self.getDate(firstElement)

        if dateElement is None:
            self.io_print('[x] warning: Error scrapping internal boletin date, proceeding with parser')
        #else:
            #self.io_print('* Date will be extracted from: ' + str(dateElement))
        self.DB_ENTRIES_tmp[DB_fecha_boletin]   = dateElement
        # get jury and branch
        if self.zone == 'Baja California':
            self.DB_ENTRIES_tmp[DB_juzgado] = 'H. Tribunal Superior de Justicia'
        else:
            jury, branch = self.getJuzgadoandRamo(firstElement)
            if jury == 'N/A' and branch == 'N/A':
                self.io_print('[x] Error scrapping internal boletin juzgado and ramo, terminating parser')
                # [kill condition] use raise?
                return False
            self.DB_ENTRIES_tmp[DB_juzgado] = jury
            self.DB_ENTRIES_tmp[DB_ramo]    = branch
        #self.io_print('*  Move to next span/text: ' + firstElement.find_next('span').text)
        self.next_element = firstElement.find_next('span')
        # issue158: validating that after finding the jury we moved to the expected position.
        while 'JUZGADO' in str(self.next_element.parent):
            self.next_element = self.next_element.find_next('span')
        self.next_element = self.jumpBlanckSpots(self.next_element, 'span')
        if self.zone == 'Baja California':
            self.idx_level = LVL_RAMO
        else:
            self.idx_level = LVL_SS
        self.validData = False

    def firstElement(self, soup):
        self.io_print('* == Searching first element: JUZGADO PRIMERO ETC ETC ==')
        keywords = self.getKeywordsFirstElement()
        for keyword in keywords:
            self.io_print('* --> Searching keyword: ' + keyword)
            try:
                firstElement = soup.find_all(text = re.compile(keyword))
                if not firstElement:
                    #self.io_print('[x] No match at all for keyword: ' + keyword)
                    continue
            except:
                self.io_print('soup error debug me')
                # [unexpected] terminate parser from caller.
                return None
            #self.io_print( firstElement)
            for firstElement in firstElement:
                if self.validateFirstElement(firstElement, keyword) != None:
                    return firstElement
            else:
                #self.io_print('\t ---> [x] Not same, dont validate')
                continue
        # [unexpected] terminate parser from caller.
        return None

    def validateFirstElement(self, firstElement, keyword):
        option_clean = self.splitandmergeText(firstElement)
        #self.io_print(' * ---> First element candidate: ' + str(option_clean))
        if re.match(r'Juzgado \w+ (?:De Paz |)Civil(?: De|,|.|) \w+', option_clean) or re.match(r'Juzgado \w+ \w+ \w+ \w+ \w+ \w+ Civil, \w+', option_clean) or \
        re.match(r'Juzgado \w+ \w+ \w+ \w+ Civil, \w+', option_clean) or \
        (self.zone == 'Tecate' and (\
        re.match(r'Juzgado De (?:Primera|1Era) (?:Inst[.]Civil|Inst[.] Civil,|Instancia Civil(?:[.]|,|' +')) Tecat\w+', option_clean) or \
        re.match(r'Juzgado \w+ \w+ \w+ \w+, Tecate, Baja California A \d+ \w+ \w+ \d+$', option_clean) or \
        # sometimes the keyword comes crippled, this can be valid also look for it
        re.match(r'Juzgado \w+ (?:Primera|1Era) Inst[.]Civil Tecate, B[.]C[.], (?:\d+|Del \d+ Y)$', option_clean) or \
        (('CIVIL(?: |\\r\\n)TECATE,' == keyword or 'TECATE,' == keyword) and str(firstElement.find_parent()).find('JUZGADO') > -1 and str(firstElement.find_parent()).find('INSTANCIA') > -1))):
            #self.io_print('\t\t* ---> [valid] Same as keyword, no validation method yet')
            return firstElement
        elif self.zone == 'Baja California' and (\
        re.match(r'(?:H.|.|)(?: |)(?:Tr\w+ |)Sup\w+ De Justicia Del Estado De(?:$| Baja Cali\w+$)', option_clean) or (\
        re.match(r'Superior De Justicia Del Estado De$', option_clean) and
        re.match(r'BAJA(?:\r\n|)(?: |  |)CALIFORNIA$',str(firstElement.find_next('st1:state'))))):
            self.io_print('\t* ---> Entering Validation method...')
            next_element = firstElement.find_next('span')
            # self.io_print(next_element.text)
            # Validate first element by moving to next span and checking that is a level 1 option
            idx_level = LVL_RAMO
            next_element = self.jumpBlanckSpots(next_element, 'span')
            text = next_element.text
            # Check if text have new lines and clear them to have a clean string
            # and safely compare against 'level_options'
            cleanText = self.splitandmergeText(text)
            validElement = False
            for option in levelOptions[idx_level]:
                foundOption = cleanText.find(option)
                if foundOption != -1:
                    # self.io_print('* ----> Pass validation found option: ' + cleanText)
                    self.io_print('\t [valid] first element: ' + firstElement)
                    validElement = True
                    break
            if not validElement:
                self.io_print('\t [x] [Invalid] first element: ' + cleanText)
                # Here we probably want to keep searching for TBS firstElement but for now let's return None
                return None
            return firstElement
        elif 'Mixtos' in self.zone:
            if re.match(r'CIUDAD MORELOS, BAJA\\r\\nCALIFORNIA', keyword):
                if re.match(r'JUZGADO MIXTO DE PRIMERA\r\nINSTANCIA', firstElement.find_previous('span').find_previous('span').text):
                    print 'test'
                else:
                    print 'Error'
                    return None
            if len(option_clean) > 100:
                return None
            self.io_print('\t [valid] first element: ' + firstElement)
            return firstElement

    def getKeywordsFirstElement(self):
        if self.zone == 'Baja California':
            keywords = keys.firstTBS_keywords
        elif self.zone == 'Tijuana':
            keywords = keys.firstTJ_keywords
        elif self.zone == 'Mexicali':
            keywords = keys.firstMXL_keywords
        elif self.zone == 'Ensenada':
            keywords = keys.firstENS_keywords
        elif self.zone == 'Tecate':
            keywords = keys.firstTCT_keywords
        elif self.zone == 'Mixtos_cdmorelos':
            keywords = keys.firstMXT_cdmorelos_keywords
            self.city = 'Ciudad Morelos'
        elif self.zone == 'Mixtos_Rosarito':
            keywords = keys.firstMXT_Rosarito_keywords
            self.city = 'Rosarito'
        elif self.zone == 'Mixtos_SanFelipe':
            keywords = keys.firstMXT_SanFelipe_keywords
            self.city = 'San Felipe'
        elif self.zone == 'Mixtos_SanQuintin':
            keywords = keys.firstMXT_SanQuintin_keywords
            self.city = 'San Quintin'
        elif self.zone == 'Mixtos_GuadalupeV':
            keywords = keys.firstMXT_GuadalupeV_keywords
            self.city = 'Guadalupe Victoria'
        else:
            # [kill condition] use raise?
            exit()
        return keywords

    def getDate(self, option):
        date_clean = self.splitandmergeText(option)
        #print date_clean
        # Catching following patterns (examples):
        # 1) JUZGADO PRIMERO CIVIL TIJUANA, B.C., 12 DE DIC. DE 2017 : '\w+ \w+ \w+ \w+, \w.\w., \d+ \w+ \w+. \w+ \d+'
        pattern1 = re.match(r'\w+ \w+ \w+ \w+, \w.\w., \d+ \w+ \w+[.] \w+ \d+', date_clean)
        # 2) JUZGADO PRIMERO CIVIL DE MEXICALI, B.C. 12 DE DICIEMBRE DE 2017: '\w+ \w+ \w+ \w+ \w+, \w.\w. \d+ \w+ \w+ \w+ \d+'
        pattern2 = re.match(r'\w+ \w+ \w+ \w+ \w+, \w.\w. \d+ \w+ \w+ \w+ \d+', date_clean)
        # 3) JUZGADO PRIMERO CIVIL DE MEXICALI, B.C. DEL 16 DE NOVIEMBRE DE 2017: '\w+ \w+ \w+ \w+ \w+, \w.\w. \w\w\w \d+ \w+ \w+ \w\w \d+'
        pattern3 = re.match(r'\w+ \w+ \w+ \w+ \w+, \w.\w. \w+ \d+ \w+ \w+ \w+ \d+', date_clean)
        # 4) JUZGADO PRIMERO CIVIL TIJUANA, B.C., 12 DE DICIEMBRE DE 2017 : '\w+ \w+ \w+ \w+, \w.\w., \d+ \w+ \w+. \w+ \d+'
        pattern4 = re.match(r'\w+ \w+ \w+ \w+, \w.\w., \d+ \w+ \w+ \w+ \d+', date_clean)
        # 5) JUZGADO PRIMERO CIVIL TIJUANA, B.C., DEL 6 DE OCT. DE 2017: '\w+ \w+ \w+ \w+, \w.\w., \w+ \d+ \w+ \w+[.] \w+ \d+'
        pattern5 = re.match(r'\w+ \w+ \w+ \w+, \w.\w., \w+ \d+ \w+ \w+[.] \w+ \d+', date_clean)
        # 6) JUZGADO PRIMERO CIVIL ENSENADA, B.C., 13 Y 14 DE JUNIO DE 2017: '\w+ \w+ \w+ \w+, \w.\w., \d+ \w \d+ \w+ \w+ \w+ \d+'
        pattern6 = re.match(r'\w+ \w+ \w+ \w+, \w.\w., \d+ \w \d+ \w+ \w+ \w+ \d+', date_clean)
        # 7) JUZGADO SEPTIMO DE PRIMERA INSTANCIA DE LO CIVIL, MEXICALI, B. C. 08 DE JULIO DE 2016
        pattern7 = re.match(r'\w+ \w+ \w+ \w+ \w+ \w+ \w+ \w+, \w+, \w. \w. \d+ \w+ \w+ \w+ \d+', date_clean)

        if   pattern1:
            #print "1"
            match = re.search(r'\w+ \w+ \w+ \w+, \w.\w., (\d+) \w+ (\w+)[.] \w+ (\d+)', date_clean)
        elif pattern2:
            #print "2"
            match = re.search(r'\w+ \w+ \w+ \w+ \w+, \w.\w. (\d+) \w+ (\w+) \w+ (\d+)', date_clean)
        # elif re.match(r'\w+ \w+ \w+ \w+ \w+, \w.\w. \d+ \w+ \w+ \w+ \d+', date_clean):
        #     match = re.search(r'\w+ \w+ \w+ \w+ \w+, \w.\w. (\d+) \w+ (\w+) \w+ (\d+)', date_clean)
        elif pattern3:
            #print "3"
            match = re.search(r'\w+ \w+ \w+ \w+ \w+, \w.\w. \w\w\w (\d+) \w+ (\w+) \w\w (\d+)', date_clean)
        elif pattern4:
            #print "4"
            match = re.search(r'\w+ \w+ \w+ \w+, \w.\w., (\d+) \w+ (\w+) \w+ (\d+)', date_clean)
        elif pattern5:
            #print "5"
            match = re.search(r'\w+ \w+ \w+ \w+, \w.\w., \w+ (\d+) \w+ (\w+)[.] \w+ (\d+)', date_clean)
        elif pattern6:
            #print "6"
            match = re.search(r'\w+ \w+ \w+ \w+, \w.\w., (\d+) \w \d+ \w+ (\w+) \w+ (\d+)', date_clean)
        elif pattern7:
            #print "7"
            match = re.search(r'\w+ \w+ \w+ \w+ \w+ \w+ \w+ \w+, \w+, \w. \w. (\d+) \w+ (\w+) \w+ (\d+)', date_clean)
        else:
            return None
        month = match.group(2)
        if   month == "Noviembre"  or month == 'Nov':
            month = "11"
        elif month == "Diciembre"  or month == 'Dic':
            month = "12"
        elif month == "Enero"      or month == 'Ene':
            month = "1"
        elif month == "Febrero"    or month == 'Feb':
            month = "2"
        elif month == "Marzo"      or month == 'Mar':
            month = "3"
        elif month == "Abril"      or month == 'Abr':
            month = "4"
        elif month == "Mayo"       or month == 'May':
            month = "5"
        elif month == "Junio"      or month == 'Jun':
            month = "6"
        elif month == "Julio"      or month == 'Jul':
            month = "7"
        elif month == "Agosto"     or month == 'Ago':
            month = "8"
        elif month == "Septiembre" or month == 'Sept' or month == 'Sep':
            month = "9"
        elif month == "Octubre"    or month == 'Oct':
            month = "10"
        else:
            return None
        day   = match.group(1)
        year  = match.group(3)
        #self.io_print(("* ----> [valid] Date: " + day + "-" + month + "-" + year))
        date = day + "-" + month + "-" + year
        #convert to DATE object to store in DB
        formula = '%d-%m-%Y'
        dateobj = datetime.datetime.strptime(date, formula)
        return dateobj.date()

    def getJuzgadoandRamo(self, option):
        option_clean     = self.splitandmergeText(option)
        keywordsJuzgados = [ 'Primero', 'Segundo', 'Tercero', 'Cuarto', 'Quinto', 'Sexto', 'Septimo', 'Octavo', 'Noveno', 'Decimo', 'Primera Instancia', '1Era Inst.Civil' ]
        keywordsRamo     = [ 'Civil', 'Familiar', 'De Paz', 'Mixto']
        if option_clean.find("Juzgado") > -1 or \
        self.zone == 'Mixtos_Rosarito' and option_clean.find("Mixto") > -1:
            for each in keywordsJuzgados:
                # 8 is the position where "juzgado" must be so we expect this to be returned by find.
                if option_clean.find(each) == 8 or (each == 'Primera Instancia' and option_clean.find(each) > -1) or \
                (each == '1Era Inst.Civil' and option_clean.find(each) != -1):
                    #self.io_print("Valid Juzgado: " + each)
                    juzgado = each
                    # Check if this is not a Decimo Primero, Segundo, etc...
                    if each == "Decimo":
                        for each in keywordsJuzgados:
                            # If we are at Sexto exit, there are not more than DECIMO SEGUNDO, letting it loop a bit more just in case
                            if each == "Sexto":
                                break
                            if option_clean.find(each) > -1:
                                juzgado = juzgado + " " + each
                                break
                    elif each == '1Era Inst.Civil':
                        return unicode('Primera Instancia'), unicode('Civil')
                    for each in keywordsRamo:
                        if option_clean.find(each) > -1:
                            ramo = each
                            return unicode(juzgado), unicode(ramo)
        # We expect that the option we are receiving is already been validated in some way so if for some reason
        # this fails we will terminate the parse
        self.io_print('[x] Unexpected option: ' + option)
        self.io_print('[x] Ending parse...')
        # [kill condition] return 'N/A'???
        exit()

    def scanContent(self):
        if self.zone == 'Mixtos_SanFelipe':
            self.mixtos_flat_text = False
        for option in levelOptions[self.idx_level]:
            # Check if text have new lines and clear them to have a clean string
            # and safely compare against 'level_options'
            foundOption = self.splitandmergeText(self.next_element.text).find(option)
            #self.io_print(('---> Looking for option: ' + option + ' in text: ' + cleanText))
            # if there is no 'Acuerdo' then let's hardcoded and continue to see if there are resolutions
            # and the 'acuerdo' tag was missed.
            if self.idx_level == LVL_TIPO and foundOption > 0:
                self.storeOptionInDB(self.idx_level, 'Acuerdos')
                self.next_element = self.next_element.find_previous('p')
                foundOption = 1

            if foundOption > -1:
                self.expectedFlow()
                return True
            else:
                self.optionSwitch = False
                self.validData = False
        else:
            return self.unexpectedFlow()
    def expectedFlow(self):
        cleanText = self.splitandmergeText(self.next_element.text)
        self.io_print('----> :) Found option: ' + cleanText)
        # Here if we are at LVL_AUTO searching a jury, and found the correct option
        # we need to adjust and make sure to move to LVL_SS (2) and not LVL_RAMO (1)
        if self.idx_level == LVL_AUTO:
            self.storeOptionInDB(self.idx_level, cleanText)
            self.idx_level += 1
        elif self.idx_level == LVL_SS:
            self.storeOptionInDB(self.idx_level, cleanText)
            self.optionSwitch = True
            self.validData = True
            return True
        elif self.idx_level == LVL_TIPO:
            self.storeOptionInDB(self.idx_level, cleanText)
            # If we are at tipo de resolucion, then let's check if resolutions are
            # as a list on a table or a list of text.
            # True when tag is at position 0 (start of string), otherwise check if it's a table.
            if str(self.next_element.find_next_sibling()).find('<p class=\"MsoNormal\">') == 0 or \
                (self.zone == 'Mixtos_SanFelipe' and self.mixtos_flat_text == True):
                self.next_element = self.next_element.find_next('p')
                flow = 'text'
            elif str(self.next_element.find_next_sibling()).find('<table') == 0:
                self.next_element = self.next_element.find_next('p')
                self.next_element = self.jumpBlanckSpots(self.next_element, 'p')
                flow = 'table'
            elif self.zone == 'Mixtos_SanFelipe' and self.mixtos_flat_text == True:
                self.io_print('[x] exit unexpected list of resolutions bug, check me.')
                return
            else:
                self.io_print('[x] exit unexpected list of resolutions, check me.')
                return
            while (self.pullResolutions(flow)):
                continue
            return True
        self.optionSwitch = True
        self.validData = True
        return True
    def unexpectedFlow(self):
        # Aqui arreglar error 170823 en tijuana
        # Patching issue#50
        #
        # We expect:
        # == JUZGADO PRIMERO ETC ETC
        # == PRIMERA SALA
        # == Acuerdos
        # == 1     1234/16     TEXTO
        # == 2     1234/12     TEXTO
        #
        # Corner case:
        # == JUZGADO PRIMERO ETC ETC
        # == Acuerdos                    <----- out of sync
        # == 1     1234/16     TEXTO
        # == 2     1235/17     TEXTO
        # == PRIMERA SALA                <----- out of sync
        # == 3     3456/25     TEXTO
        #
        if self.idx_level == LVL_SS:
            for option in levelOptions[LVL_TIPO]:
                foundOption = self.splitandmergeText(self.next_element.text).find(option)
                #self.io_print(('---> Looking for option: ' + option + ' in text: ' + self.splitandmergeText(self.next_element.text)))
                if foundOption == 0:
                    self.io_print('#Executin patch#50 to get in sync with Sala')
                    self.optionSwitch = True
                    self.validData = False
                    self.idx_level = LVL_TIPO
                    # Move next_element from:
                    # Corner case:
                    # == JUZGADO PRIMERO ETC ETC
                    # == Acuerdos                    <----- next_element should point here
                    # == 1     1234/16     TEXTO     <----- tmp should point here after finding next 'span'
                    # == 2     1235/17     TEXTO
                    # == PRIMERA SALA                <----- We will loop until we found this
                    # == 3     3456/25     TEXTO
                    tmp = self.next_element.find_next('span')
                    # Loop until we find the secretaria
                    loop = True
                    # Let's limit the loop to 15 iterations, after that we will add a default 'SALA'
                    # set a flag and keep looping to the next level.
                    try:
                        loopCounter = 0
                        while loop:
                            loopCounter = loopCounter + 1
                            tmp = tmp.next_element.find_next('span')
                            for option in levelOptions[LVL_SS]:
                                cleanText = self.splitandmergeText(tmp.text)
                                foundOption = cleanText.find(option)
                                #self.io_print(('---> Looking for option: ' + option + ' in text: ' + cleanText))
                                if foundOption != -1 and foundOption < 32 and re.match(r'\w+ Secretaria', cleanText):
                                    self.storeOptionInDB(LVL_SS, cleanText)
                                    loop = False
                                    break
                                elif loopCounter ==15:
                                    self.storeOptionInDB(LVL_SS, 'Primera Secretaria')
                                    if self.zone == 'Mixtos_SanFelipe':
                                        mixtos_flat_text = True
                                    loop = False
                                    break
                        return True
                    except:
                        self.io_print('Patch#50 failed for unknown reasons, the best is to exit')
                        return False
                    break
        # Patch :
        # Handling case where no "Tipo de resolucion" exists after a "Secretaria", we check if what is pointing
        # is a digit(Numero de Resolucion) to proceed with parsing, if not then exit with an error, this will help to catch further
        # things we need to handle. If no "Tipo de resolucion" exists the default will be "Acuerdos"
            else:
#                         # This means there is no 'secretaria'
#                         # The following data can be a type of acuerdo or
#                         # a file row or
#                         # trash data like chuncks of other texts
#                         # Corner case:
#                         # == JUZGADO PRIMERO ETC ETC
#                         # == Acuerdos ??? <---- Check if acuerdo is present or
#                         # == 1     1234/16     TEXTO     <----- Check if file row is present
#                         # == 2     1235/17     TEXTO
#                         # if the data we are checking is not the expected for example (170109sanfelipe)
                if self.splitandmergeText(self.next_element.text)[0].isdigit():
                    self.io_print('----> :o Corner case: No "Sala" default option: ' + 'Primera Sala')
                    self.storeOptionInDB(self.idx_level, 'Primera Sala')
                    self.storeOptionInDB(self.idx_level+1, 'Acuerdos')
                    while (self.pullResolutions(flow = 'text')):
                        continue
                else:
                    self.io_print('text')
                return True
        elif self.idx_level == LVL_TIPO:
            if self.next_element.text[0].isdigit() or self.zone == 'Baja California' and re.match(r'N-\w+',self.next_element.text):
                self.io_print('----> :o Corner case: No "Tipo de Resolucion" default option: ' + 'Acuerdos')
                self.storeOptionInDB(self.idx_level, 'Acuerdos')
                flow = None
                # If we are at tipo de resolucion, then let's check if resolutions are
                # as a list on a table or a list of text.
                # True when tag is at position 0 (start of string), otherwise check if it's a table.
                if str(self.next_element.find_next_sibling()).find('<p class=\"MsoNormal\">') == 0 or \
                    (self.zone == 'Mixtos_SanFelipe' and mixtos_flat_text == True):
                    #self.next_element = self.next_element.find_next('p')
                    flow = 'text'
                elif str(self.next_element.find_next_sibling()).find('<table') == 0:
                    #self.next_element = self.next_element.find_next('p')
                    #self.next_element = self.jumpBlanckSpots(self.next_element, 'p')
                    flow = 'table'
                elif self.zone == 'Mixtos_SanFelipe' and mixtos_flat_text == True:
                    self.io_print('[x] exit unexpected list of resolutions bug, check me.')
                    return False
                else:
                    flow = 'table'
                while (self.pullResolutions(flow)):
                    continue
                return True
    def moveChips(self):
        #self.io_print("Switches state, optionSwitch=" + str(self.optionSwitch) + " validData = " + str(self.validData))
        if self.optionSwitch == self.validData:
            self.next_element = self.next_element.find_next('p')
            self.next_element = self.jumpBlanckSpots(self.next_element, 'p')
        # This means we had a valid data for the level we are at, expect to move to next span and next level
        if self.optionSwitch is True and self.validData is True:
            #self.io_print("vd:moving to next span")
            self.idx_level += 1
            #self.io_print("increasing idx_level")
            if self.idx_level > LVL_TIPO:
                #self.io_print("resetting search")
                self.idx_level = LVL_AUTO
        # This means we have not found a valid data, so move to next span but not level,
        # unless you are already at level 3 we reset, hmmm...
        elif self.optionSwitch is False and self.validData is False:
            if self.idx_level > LVL_TIPO:
                #self.io_print("resetting search")
                self.idx_level = LVL_AUTO
        else:
            pass
            # these means we already move our chips and don't want to move the switches as usual.
            #self.io_print("--> not moving switches")

    # ============= PULL RESOLUTIONS ================
    # Each boletin is segmentated by Jurys and Rooms,
    # Each rooms releases a series of resolutions that get categorized by types of
    # resolution, then each category have the following data in the expected order:
    # [ No. Resolution (Numeric) - No. File (Alphanumeric) - Description (Text)
    #
    # This info will need to be scraped and stored in self.DB_ENTRIES_tmp
    def pullResolutions(self, flow = 'None'):
        # We are expecting a digit representing the count of resolutions
        if flow == 'text':
            resolution = self.splitandmergeText(self.next_element.text)
            if self.zone == 'Mixtos_cdmorelos':
                # Try clean up for cases like:
                # '5.- Exp.- 269/15 Alberto Vega Retcetc' or
                # '1.- Exp. 176/04 JESS FRANCetcetc'
                if 'Exp.' in resolution:
                    resolution = resolution.replace('.-','').replace('Exp.','')
                elif 'Exp.-' in resolution:
                    resolution = resolution.replace('.-','').replace('Exp','')
            elif self.zone == 'Mixtos_SanFelipe':
                # Try clean up for cases like(170425):
                # '1.- 293/2015 SUCESORIO INTESTAMENTARIO A BIENES DE MIGUEL CUEVAS MEZA.'
                resolution = resolution.replace('.-','')
            self.DB_ENTRIES_tmp[DB_nr] = resolution.split()[0]
            self.DB_ENTRIES_tmp[DB_ne] = resolution.split()[1]
            tmp_split = resolution.split()
            self.DB_ENTRIES_tmp[DB_contenido] = ' '.join(tmp_split[2:])
            #self.io_print(self.DB_ENTRIES_tmp)
            copy = self.DB_ENTRIES_tmp[:]

            # [COPY TMP DATA TO MASTER ARRAY DB_ENTRIES]
            self.DB_ENTRIES.append(copy)

            self.next_element = self.next_element.find_next("p")
            self.next_element = self.jumpBlanckSpots(self.next_element, 'p')
            cleanStopCondText = self.splitandmergeText(self.next_element.text)
            # Condition to stop inserting expedientes to DB
            cleanStopCondText = cleanStopCondText.rstrip(':')
            self.io_print(self.DB_ENTRIES_tmp)
            if not self.checkStopCondition(cleanStopCondText):
                #self.io_print('---> continue getting resolutions')
                return True
            else:
                return False
        if not self.splitandmergeText(self.next_element.text.replace('.','')).isdigit():
            # There is a bug where a lot of empty td's appear,
            # if td content is empty lets try to sync
            if len(self.splitandmergeText(self.next_element.find_next('td').text)) <= 0:
                inSync = False
                while (not inSync):
                    self.next_element = self.next_element.find_next('td')
                    if not len(self.splitandmergeText(self.next_element.text)) <= 0:
                        inSync = True
            else:
                # if for some reason we end up here, terminate unless next element is a file number.
                if self.next_element.text.find('/') > -1:
                    self.io_print("Woow, entering to corner case... Be careful D= : " + self.next_element.text.strip())
                    self.DB_ENTRIES_tmp[DB_nr] = ''
                else:
                    exit()
        else:
            self.DB_ENTRIES_tmp[DB_nr] = self.next_element.text.strip()
            self.next_element = self.next_element.find_next('td')
        # Let's try to catch if there are inconsistencies here just if
        # object is empty
        if len(self.next_element.find_next('td').contents) <= 0:
            inSync = False
            while (not inSync):
                self.next_element = self.next_element.find_next('td')
                if not len(self.next_element.contents) <= 0:
                    inSync = True
        # 1) [NUMERO DE RESOLUCION EN LA HOJA]
        # It can happen that instead of having the expected count number, we will encounter the file number,
        # we can detect this if a forward slash
        if re.match(r'\d+|\d+\w+\/\d+$',self.splitandmergeText(self.next_element.text)):
            # 2) [NUMERO DE EXPEDIENTE]
            self.DB_ENTRIES_tmp[DB_ne] = self.next_element.text.strip()
        else:
            # Maybe there is a valid inconsistency, like a typo
            # detect it and keep going.
            # If the next 'td' is a text then maybe we are at a typo, let's try to continue
            if len(self.next_element.find_next('td').contents) > 0:
                if len(self.next_element.contents) > 0:
                    self.DB_ENTRIES_tmp[DB_ne] = self.splitandmergeText(self.next_element.text)
                else:
                    self.DB_ENTRIES_tmp[DB_ne] = 'N/A'
            else:
                exit()
        # Let's try to catch if there are inconsistencies here just if
        # object is empty
        if len(self.next_element.find_next('td').contents) <= 0:
            inSync = False
            while (not inSync):
                self.next_element = self.next_element.find_next('td')
                if not len(self.next_element.contents) <= 0:
                    inSync = True
        self.next_element = self.next_element.find_next('td')
        # 3) [PARTES]
        if len(self.next_element.contents) > 0:
            self.DB_ENTRIES_tmp[DB_contenido] = self.splitandmergeText(self.next_element.text)
        else:
            exit()
        #self.io_print(self.DB_ENTRIES_tmp)
        copy = self.DB_ENTRIES_tmp[:]

        # [COPY TMP DATA TO MASTER ARRAY DB_ENTRIES]
        self.DB_ENTRIES.append(copy)

        self.next_element = self.next_element.find_next("p").find_next("p")
        self.next_element = self.jumpBlanckSpots(self.next_element, 'p')
        cleanStopCondText = self.splitandmergeText(self.next_element.text)
        # Condition to stop inserting expedientes to DB
        cleanStopCondText = cleanStopCondText.rstrip(':')
        if not self.checkStopCondition(cleanStopCondText):
            #if self.debug_all:
            #    self.io_print('---> continue getting resolutions')
            return True
        else:
            return False
    def checkStopCondition(self, stopCond):
        # valid stop conditions can be:
        # A 'firma' like 'EL C. SECRETARIO DE ACUERDOS LIC. JOSE BENITO GUTIERREZ PEREZ'
        # A 'Secretaria' any 'Example Secretaria' should be treated as valid stop condition
        # A 'Juzgado' any 'Juzgado Primero bla bla bla'
        #
        # Invalid stop conditions:
        # A 'numero de resolucion' this is always a digit
        # A 'tipo de expediente'
        if not stopCond.isdigit() and not (self.zone == 'Baja California' and re.match(r'N-\w+',stopCond)):
            #self.io_print("---> Checking condition: " + stopCond)
            # Here we check a couple things:
            # 1) check if stop condition was triggered by a level 3 option
            for option in levelOptions[LVL_TIPO]:
                if stopCond.find(option) == 0 and (re.match(r'\w+$', stopCond) or re.match(r'\w+ \w+$', stopCond) or re.match(r'Cuadernos \w+ \w+$', stopCond)):
                    #self.io_print("----> update tipo de expediente: " + self.splitandmergeText(stopCond))
                    self.io_print('----> :) Found option: ' + self.splitandmergeText(self.next_element.text))
                    self.DB_ENTRIES_tmp[DB_tipo] = self.splitandmergeText(stopCond)
                    self.next_element = self.next_element.find_next("p")
                    return False
            else:
                tmp_elm = self.next_element.find_next("p")
                tmp_elm = self.jumpBlanckSpots(tmp_elm, 'p')
                # Maybe any LVL_TIPO was found because we don't support it, let's keep scraping if this is the case.
                if re.match(r'[\d+|\d+\w+]\/\d+$',self.splitandmergeText(tmp_elm.text)) and self.splitandmergeText(tmp_elm.text).isdigit():
                    self.io_print("!!--> not supported tipo de expediente: " + self.splitandmergeText(stopCond))
                    self.DB_ENTRIES_tmp[DB_tipo] = self.splitandmergeText(stopCond)
                    self.next_element = tmp_elm
                    return False
            # Any of the next conditions if true will exit pullResolutions
            # 2) check if stop condition was triggered by a level 2 option
            for option in levelOptions[LVL_SS]:
                if stopCond.find(option) > -1 and re.match(r'\w+ (?:Secretaria|Secretaria Civil|Sala)$', stopCond):
                    #self.io_print("----> out of sync, look for a SECRETARIA")
                    self.idx_level    = LVL_SS
                    break
            else:
                # 3) check if stop condition was triggered by a level 1 option ONLY TBS, pending to ifdef
                for option in levelOptions[LVL_RAMO]:
                    if stopCond.find(option) != -1:
                        #self.next_element = self.next_element.find_next("p").find_next("p")
                        self.idx_level    = LVL_RAMO
                        break
                else:
                    if re.search(r'[Secretar\w+|Secretar\w+ General] De Acue\w+', stopCond):
                        #self.bar.update(i_progress)
                        #sleep(0.1)
                        #self.io_print("--> The end of pulling acuerdos, firma found, move to next...")
                        self.next_element = self.next_element.find_next("p")
                        stopCond = self.splitandmergeText(self.next_element.text)
                        while stopCond == '':
                            self.next_element = self.next_element.find_next("p")
                            stopCond = self.splitandmergeText(self.next_element.text)
                    else:
                        self.io_print('[!] NO FIRMA at the end of boletines from sala!!!')
                        self.next_element = self.jumpBlanckSpots(self.next_element, 'p')
                    stopCond = self.splitandmergeText(self.next_element.text)
                    # Maybe patch here for empty spots, if we don't find a jury then try EDICTO
                    for option in levelOptions[LVL_AUTO]:
                        if stopCond.find(option) != -1:
                            #self.io_print("---> out of sync, look for a JUZGADO")
                            self.idx_level = LVL_AUTO
                            break
                    else:
                        if stopCond.find('E D I C T O') != -1:
                            self.optionSwitch = True
                            self.validData = False
                        elif stopCond.find('Baja California A') != -1:
                            # This should be only for TBS, exit condition sync.
                            self.next_element = self.next_element.find_next("p").find_next("p").find_next("p")
                            self.idx_level = LVL_AUTO
                            self.optionSwitch = True
                            self.validData = False
                            return True
                            stopCond = self.splitandmergeText(self.next_element.text)
                            for option in levelOptions[LVL_AUTO]:
                                if stopCond.find(option) != -1:
                                    #self.io_print("---> out of sync, look for a JUZGADO")
                                    self.idx_level = LVL_AUTO
                                    self.optionSwitch = True
                                    self.validData = False
                                    return True
                        else:
                            self.io_print('[x] Error unexpected exit condition')
                            exit()
            if self.idx_level != LVL_TIPO:
                self.optionSwitch = True
                self.validData = False
                return True
            return False
        return False
    def jumpBlanckSpots(self, next_element, jumpType):
        element = self.splitandmergeText(next_element.text)
        while not element:
            #print "corner case move more to go to a valid data:", self.DB_ENTRIES_tmp[DB_ne]
            # print self.next_element.find_next("p").find_next("p").find_next("p").text
            next_element = next_element.find_next(jumpType)
            element = self.splitandmergeText(next_element.text)
        return next_element
    def splitandmergeText(self, text):
        if "\n" in text:
            cleanText = text.split()
            #self.io_print("---> !fix Text: ", ' '.join(cleanText))
            cleanText = ' '.join(cleanText)
        else:
            cleanText = text.strip()
        # Fix bug where juzgado was found like : H.&nbsp;TRIBUNAL&nbsp;SUPERIOR etc...
        return cleanText.replace(u'\xa0', ' ').title()
    def storeOptionInDB(self, idx_level, option):
        option = option
        if idx_level == LVL_AUTO:
            # NOTE: currently this option is noly valid for Tijuana, in here it will
            # try to get "juzgado" and "ramo" from string "option"
            self.DB_ENTRIES_tmp[DB_juzgado], foo = self.getJuzgadoandRamo(option)
            foo, self.DB_ENTRIES_tmp[DB_ramo]    = self.getJuzgadoandRamo(option)
            #if IO_DEBUG > 0:
            #    print "*  Pull Autoridad for DB"
        elif idx_level == LVL_RAMO:
            self.DB_ENTRIES_tmp[DB_ramo] = option.title()
            # if IO_DEBUG > 0:
            #     print "*  Pull Ramo for DB"
        elif idx_level == LVL_SS:
            self.DB_ENTRIES_tmp[DB_ss] = option.title()
            # if IO_DEBUG > 0:
            #     print "*  Pull Sala for DB"
        elif idx_level == LVL_TIPO:
            self.DB_ENTRIES_tmp[DB_tipo] = option.title()
            # if IO_DEBUG > 0:
            #     print "*  Pull Tipo de Resolucion for DB"
        else:
            self.io_print("[x] Unexpected level: " + idx_level + " bug in algorithm?")

    # ============= PARSE DAILY ================
    # Methods to execute daily task for scraping any released 'boletin'
    # Initial conditions good to know:
    #   1) A new 'boletin' is released for every work day in the calendar for BC.
    #   2) Every new 'boletin' is released by 2pm
    # 'boletines' are released in the following way:
    # The 'boletin' that is being released the current work day is publishing data that will be
    # available for lawyers the next work day meaning the following:
    # under construction/...
    #
    # ---> parse_daily()
    #      - Check if a 'boletin' exists today;
    #      |   --Try to find next work day and scrape it;
    #      |   |    check_and_notify_users()
    #      |   |    notify_android_users()
    #      |   |    notify_email_report()
    #      |   |    THE END.
    #      |   |
    #      |   \-> if not try to find the next work day by moving an additional day. This can only exit
    #              without scraping if we are at december holidays.
    #       \-> if not we are probably at a weekend or holiday. return.
    def parse_daily(self):
        self.year  = datetime.datetime.today().strftime('%Y')
        self.year  = int(self.year[-2:])
        self.month = int(datetime.datetime.today().strftime('%m'))
        self.day   = int(datetime.datetime.today().strftime('%d'))
        self.io_print('\n==== STARTING PARSE DAILY ====')
        self.io_print('\tScrapping \"Boletin\" that was released today: %d/%d/%d BC' % (self.day, self.month, self.year))
        FRIDAY    = 4 # TODO: add the proper way of getting the value of friday from datetime class.
        dayofweek = datetime.datetime.today().weekday()
        #dayofweek = 4
        # Calculate how many days are in the testing month.
        if self.month == 12:
            self.END_OF_MONTH = (datetime.date(self.year, self.month, 1) - datetime.date(self.year, self.month - 1, 1)).days
        else:
            self.END_OF_MONTH = (datetime.date(self.year, self.month + 1, 1) - datetime.date(self.year, self.month, 1)).days
        # We don't know what exact day of the year the first boletin its posted,
        # it should be around the first 10 days of the year, try to catch it or
        # if not on the first days of the years then follow the normal flow.
        if self.month == 1 and self.day < 11:
            # Start of year flow.
            self.io_print('\t[info] Trying to find the first boletin of the year \'boletin\'.')
            # Test if boletin exists today, this mean the first of the year has been already released.
            self.io_print('\t[info] Checking if there is not already a first boletin today')
            if not self.scrapeUrl(testUrl = True):
                self.io_print('\t[!] No first boletin yet, look if was released the next work day')
                # At 4 (Friday) we move by 2 days to be at Monday, and weekends (5 and 6) no need to check them.
                if dayofweek == 4:
                    moveday = 2
                elif dayofweek == 5:
                    return
                else:
                    moveday = 1
                if not self.scrapeUrl(moveday, storeDb = True):
                    if self.day == 10:
                        self.io_print('\t[!] Unexpected condition, debug me.')
                        exit()
                    self.io_print('\t[!] No valid url for today')
                    self.io_print('\t[!] Today is not a work day, try tomorrow...\n\n\n')
                    return
                else:
                    self.io_print('\t[info] Found the first boletin of the year...')
                    return
            self.io_print('\t[!] Already found the first boletin of the year go to normal flow...')
        else:
            # Normal flow
            if not self.scrapeUrl(testUrl = True):
                # In here having a valid boletin on a weekend will be a weird case so we will need
                # to raise some warning.
                self.io_print('\t[!] Error, we are at a weekend day.')
                return
        self.it = 1
        if dayofweek < FRIDAY:
            self.io_print('\t[info] Trying to scrape a new \'boletin\'.')
            while (not self.scrapeUrl(self.it, testUrl = True)):
                self.io_print('\t[info] No boletin next weekday, probably a holiday lets try the next day')
                self.it += 1
                # return after trying 10 days.
                if self.it == 10 and self.month < 12:
                    return
            # scrapeUrl will turn on this flag
            if not self.december_vacations:
                self.io_print('\t[info] Start scrapping a new boletin.')
                self.scrapeUrl(self.it, storeDb = True)
        elif dayofweek == FRIDAY:
            self.io_print('\t[info] We are at Friday, released \'boletin\' is at minimum 2 days from now')
            self.io_print('\t[info] Test the link before scrapping, maybe we are at a long weekend')
            self.it = 3
            while (not self.scrapeUrl(self.it, testUrl = True)):
                self.io_print('\t[info] Probably a long weekend due to holiday, check next day')
                self.it += 1
                # return after trying 10 days.
                if self.it == 10 and self.month < 12:
                    return
            # scrapeUrl will turn on this flag
            if not self.december_vacations:
                self.io_print('\t[info] Start scrapping a new boletin.')
                self.scrapeUrl(self.it, storeDb = True)
        else:
            self.io_print('\t[!] No valid url for today')
            self.io_print('\t[!] Today is not a work day, try tomorrow...\n')
            #self.io_email.send_report('no_boletin_disponible', None, self.io_debug.io_getbuffer())
        # [START send_mail]
        mail.send_mail(sender="delriogjl@gmail.com",
                       to="io-admins <delriogjl@gmail.com>",
                       subject="daily boletin has been parsed",
                       body="""The daily boletin has been parsed succesfully.
        """)

    def scrapeUrl(self, moveday = 0, storeDb = False, testUrl = False):
        counterValid   = 0
        counterInvalid = 0
        tmpDay    = self.day   + moveday
        tmpMonth  = self.month
        tmpYear   = self.year
        if tmpDay > self.END_OF_MONTH:
            self.io_print('Going to next month')
            # We pass the end of the month, restart day and tmpDay to 1
            if self.END_OF_MONTH == 30 and moveday > 1:
                tmpDay = 2
                self.day    = 2
            else:
                tmpDay = 1
                self.day    = 1
            # it was made global so we can reset it from here as well, make it 0 since it should be 0 when
            # day is equal to 1.
            self.it     = 0
            # Move to next month, I don't recall seeing more than 2 months vacations
            self.month += 1
            tmpMonth = self.month
            if tmpMonth > self.LAST_MONTH:
                self.io_print('Looks like christmas vacations, bye...')
                self.december_vacations = True
                return True
        if tmpDay < 10:
            day_string = '0' + str(tmpDay)
        else:
            day_string = str(tmpDay)
        if tmpYear < 10:
            year_string = '0' + str(tmpYear)
        else:
            year_string =  str(tmpYear)
        if tmpMonth < 10:
            month_string = '0' + str(tmpMonth)
        else:
            month_string = str(tmpMonth)
        link = 'http://www.pjbc.gob.mx/boletinj/20' + year_string + '/my_html/bc' +  year_string + month_string + day_string + '.htm'
        # link = 'http://www.pjbc.gob.mx/boletinj/2018/my_html/bc180226.htm'
        if testUrl:
            self.io_print('\t-> testing link = ' + link)
        else:
            self.io_print('\t-> scrapping link = ' + link)
        try:
            html = urllib2.urlopen(link)
            # PJBC website is redirecting to home page rather than what was originally doing, replying with an 404 error.
            if html.geturl().find('boletinj') == -1:
                raise Exception('\t[!] Invalid Link')
            if testUrl:
                return True
        except Exception as error:
            self.io_print(str(error))
            return False
        else:
            self.io_print('\t[info] Found valid boletin, START SCRAPPING!!!... Yum!\n\n')
            # Check if already following boletin.
            try:
                # generate url date to store it on array
                date = day_string + "-" + month_string + "-20" + year_string
                formula = '%d-%m-%Y'
                dateobj = datetime.datetime.strptime(date, formula)
                # check if the url has been already parsed
                query = ("SELECT EXISTS( SELECT fecha_url "
                "FROM resoluciones "
                "WHERE fecha_url = '" + dateobj.strftime('%Y-%m-%d') + "' )" + ";")
                self.io_mysql.connect()
                exists = self.io_mysql.execute(query)
                if exists[0][0] != 0:
                    self.io_print('[!] This boletin has already been scraped, debug why.')
                    storeDb = False
                    return False
            finally:
                self.io_mysql.disconnect()

            try:
                self.parse_boletin(False, link)
            except:
                self.io_print("\t\t\t\t[x] Unsuccessful parse: " + link)
                self.io_print('\t[!] Try storing any valid resolution...')
                # [email failure]
                mail.send_mail(sender="delriogjl@gmail.com",
                               to="io-admins <delriogjl@gmail.com>",
                               subject="daily boletin has been parsed: FAILURE",
                               body="""The daily boletin has been parsed with a failure: PENDING TO ATTACH LOG.
                """)
                # continue
                pass
            # Here we always try to store in the DB if specified and even if parser fail we will try to store
            # any possible data in case the parser was able to run partially.
            self.io_print("\n\n\tSuccessful parsing, now time to store items in database:\n")
            if storeDb:
                self.io_mysql.connect()
            for p in self.DB_ENTRIES:
                p[0] = dateobj.date()
                #self.io_print(str(p))
                if storeDb:
                    try:
                        self.io_mysql.store_resolutions(p)
                        counterValid += 1
                    except:
                        counterInvalid += 1
                        self.io_print('\t[!] Error committing data to database: ' + str(p))
            self.io_print("\n[Commit to database finished, summary]:\n")
            self.io_print('\tcommitted: ' + str(counterValid) + ' failed: ' + str(counterInvalid) + '\n')
            #     #checkTrackingCases  ()
            #     #notifyToAndroid     () SEND_NOTIFICATION  io_notify. 
            # Note: we extract the reportID from the url like -> link[45:53] example of result: bc101018
            #self.io_email.send_report(link[45:53], self.DB_ENTRIES, self.io_debug.io_getbuffer())
            #print 'Email report sent...'
            if storeDb:
                self.io_mysql.disconnect()
            return True
