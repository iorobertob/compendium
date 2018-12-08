
# Keywords used to track down reference position when scanning zones
firstTBS_keywords = (r'(?:H.|.|)(?: |\r\n|)TR\w+(?: |\r\n|)SUPE\w+(?: |\r\n|)DE(?: |\r\n|)JUS\w+(?: |\r\n|)DEL(?: |\r\n|)ESTADO(?: |\r\n|)DE(?: |\r\n|)BAJA(?: |\r\n|)CALI\w+',
                     r'(?:H.|.|)(?: |\r\n|)TR\w+(?: |\r\n|)SUP\w+(?: |\r\n|)DE(?: |\r\n|)JUSTICIA(?: |\r\n|)DEL(?: |\r\n|)ESTADO(?: |\r\n|)DE(?: |\r\n|)',
                     r'SUPERIOR(?: |\r\n|)DE(?: |\r\n|)JUSTICIA(?: |\r\n|)DEL(?: |\r\n|)ESTADO(?: |\r\n|)DE(?: |\r\n|)',
                     r'TRIBUNAL SUPERIOR DE JUSTICIA',
                     r'SUPERIOR')

firstTJ_keywords  = (r'JUZGADO(?: |\r\n)(?:PRIMERO|TERCERO)(?: |\r\n)CIVIL(?: DE|\r\n DE|,|)(?: |\r\n)TIJUANA','NONE')

firstMXL_keywords = ( r'JUZGADO(?: |\r\n)(?:PRIMERO|SEGUNDO|TERCERO)(?: |\r\n| DE PAZ )CIVIL(?: DE|\r\n DE|,|.|)(?: |\r\n)MEXICALI',
                      r'JUZGADO\r\nSEPTIMO DE PRIMERA INSTANCIA DE LO CIVIL DE MEXICALI',
                      r'JUZGADO\r\nSEPTIMO DE PRIMERA INSTANCIA DE LO CIVIL, MEXICALI')
# firstMXL_keywords = ('JUZGADO\r\nOCTAVO DE PRIMERA INSTANCIA CIVIL, MEXICALI')
firstENS_keywords = (r'JUZGADO(?: |\r\n)\w+(?: |\r\n)CIVIL(?: |\r\n|,)(?:DE|)(?: |\r\n|)ENSENADA',
                     r'None')

firstMXT_cdmorelos_keywords = (r'JUZGADO(?: |\r\n)MIXTO(?: |\r\n)DE(?: |\r\n)PRIMERA(?: |\r\n)INSTANCIA(?: |\r\n|.|)(?:DE|,|)(?: |\r\n|)(?:CD.|CIUDAD|)(?: |\r\n)MORELOS',
                               r'None')

firstMXT_Rosarito_keywords = (r'JUZGADO(?: |\r\n|)MIXTO(?: |\r\n|)DE(?: |\r\n)(?:PRIMERA|1ERA)(?: |\r\n)(?:INSTANCIA|INST.CIVIL)(?: |\r\n|.|)(?:DE|,|)(?: |\r\n|)(?:PLAYAS|)(?: |\r\n)DE(?: |\r\n)ROSARITO',
                             r'(?:JUZGADO|)(?: |\r\n|)(?:MIXTO|)(?: |\r\n|)DE(?: |\r\n)(?:PRIMERA|1ERA)(?: |\r\n)(?:INSTANCIA|INST.CIVIL)(?: |\r\n|.|)(?:DE|,|)(?: |\r\n|)(?:PLAYAS|)(?: |\r\n)DE(?: |\r\n)ROSARITO',r'None')

firstMXT_SanQuintin_keywords = (r'JUZGADO(?: |\r\n)(?:MIXTO|)(?: |\r\n|)DE(?: |\r\n)PRIMERA(?: |\r\n)INSTANCIA(?: |\r\n|.|(?: |\r\n|)CIVIL|)(?: |\r\n|)(?:DE|,|)(?: |\r\n|)(?:SAN|)(?: |\r\n)QUINT\xcdN',
                               r'None')

firstMXT_SanFelipe_keywords = (r'JUZGADO(?: |\r\n)MIXTO(?: |\r\n)DE(?: |\r\n)PRIMERA(?: |\r\n)INSTANCIA(?: |\r\n|.|)(?:DE|,|)(?: |\r\n|)(?:SAN|)(?: |\r\n)FELIPE',
                               r'None')

firstMXT_GuadalupeV_keywords = (r'JUZGADO(?: |\r\n)DE(?: |\r\n)(?:PRIMERA|1ERA)(?: |\r\n)(?:INSTANCIA|INST.CIVIL)(?: |\r\n|.|)(?:DE|,|)(?: |\r\n|)(?:GUADALUPE|)(?: |\r\n)VICTORIA',
                               r'JUZGADO(?: |\r\n)(?:MIXTO|)(?: |\r\n|)DE(?: |\r\n)(?:PRIMERA|1ERA)(?: |\r\n)(?:INSTANCIA|INST.CIVIL)(?: |\r\n|.|)(?:DE|,|DE(?: |\r\n)LO(?: |\r\n)CIVIL(?: |\r\n)DE|)(?: |\r\n|)(?:CIUDAD|CD.)(?: |\r\n|)(?:GUADALUPE|)(?: |\r\n)VICTORIA',
                               r'JUZGADO(?: |\r\n)(?:MIXTO|)(?: |\r\n|)DE(?: |\r\n)(?:PRIMERA|1ERA)(?: |\r\n)(?:INSTANCIA|INST.CIVIL)(?: |\r\n|.|)(?:DE|,|DE(?: |\r\n)LO(?: |\r\n)CIVIL(?: |\r\n)DE|)(?: |\r\n|)(?:CIUDAD)')

firstTCT_keywords = (r'JUZGADO(?: |\r\n)DE(?: |\r\n)(?:1ERA|PRIMERA)(?: |\r\n)(?:INST.|INSTANCIA)(?: |\r\n|)CIVIL(?:,|.|)(?: |\r\n)TECATE',
    r'JUZGADO DE PRIMERA INSTANCIA\r\nCIVIL.', r'CIVIL(?: |\r\n)TECATE,', r'TECATE,')
