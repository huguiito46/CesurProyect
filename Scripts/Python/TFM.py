from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
import pandas as pd
import datetime


def extraer_datos(driver, user_linkedin, passw_linkedin, nombre_busqueda):
    if len(nombre_busqueda.split(' ')) > 2:
        nombre_busqueda = '%20'.join(
            [nombre_busqueda.split(' ')[0], nombre_busqueda.split(' ')[1], nombre_busqueda.split(' ')[2]])
    else:
        nombre_busqueda = '%20'.join([nombre_busqueda.split(' ')[0], nombre_busqueda.split(' ')[1]])

    datos = []
    driver = webdriver.Chrome(driver)

    # Obtenemos la página de login de linkedin
    driver.get('https://www.linkedin.com/login')

    time.sleep(5)

    # Introducimos el usuario de linkedin
    username = driver.find_element_by_id('username')
    username.send_keys(user_linkedin)

    # Introducimos la contrasena de linkedin
    pword = driver.find_element_by_id("password")
    pword.send_keys(passw_linkedin)

    driver.find_element_by_xpath("//button[@type='submit']").click()

    # Hacemos la búsqueda por el nombre introducido
    profile_url = "https://www.linkedin.com/search/results/people/?keywords=" + nombre_busqueda
    driver.get(profile_url)

    src = driver.page_source
    bs = BeautifulSoup(src, "html.parser")

    pagina_principal = driver.current_url

    time.sleep(3)

    buscador = bs.find_all('li', attrs={'class': 'reusable-search__result-container'})

    for item in buscador:
        link = item.find('a')['href']

        # Obtenemos la descripción
        i = item.find('div', attrs={'class': 'entity-result__primary-subtitle t-14 t-black t-normal'})
        descripcion = i.text.split("\n")[1]

        # Obtenemos la ubicación
        j = item.find('div', attrs={'class': 'entity-result__secondary-subtitle t-14 t-normal'})
        ubicacion = j.text.split("\n")[1]

        driver.get(link)

        src = driver.page_source
        bs = BeautifulSoup(src, "html.parser")

        # Obtenemos el nombre
        k = bs.find('h1', attrs={'class': 'text-heading-xlarge inline t-24 v-align-middle break-words'})

        try:
            nombre = k.text
            pattern = '\"Empresa actual\"\>\s*?[a-z-A-Z]+'
            try:
                # Obtememos la compañia
                try:
                    company = re.findall(pattern, driver.page_source)[0].split('\n\n')[1].strip()
                except:
                    time.sleep(1)
                    company = re.findall(pattern, driver.page_source)[0].split('\n\n')[1].strip()
            except:
                print('Perfil Incompleto para el Analisis')
                break

            src = driver.page_source
            soup = BeautifulSoup(src, 'html.parser')
            # Obtememos la permanencia
            dateed = soup.find_all('span', {'class': 't-14 t-normal t-black--light'})[0:2]

            if re.search('\d+', str(dateed[0]).split(r'<!-- -->')[1]):
                permanencia = str(dateed[0]).split(r'<!-- -->')[1]
                # Limpiamos los datos para obtener unicamente el valor
                permanencia = permanencia.split('·')[1]

            else:
                permanencia = str(dateed[1]).split(r'<!-- -->')[1]
                # Limpiamos los datos para obtener unicamente el valor
                permanencia = permanencia.split('·')[1]

            # Obtememos la fecha de la búsqueda
            fecha_busqueda = datetime.date.today()

            # Añadimos los datos obtenidos al array para posteriormente crear el dataframe
            datos.append([nombre, ubicacion, descripcion, company, permanencia, fecha_busqueda])

            time.sleep(3)
            driver.get(pagina_principal)
        except:
            continue

    # Creamos el dataframe que exportamos a csv
    data = pd.DataFrame(datos,
                        columns=['nombre', 'ubicacion', 'descripcion', 'company', 'permanencia', 'fecha_busqueda'])
    data.to_csv('datos_sin_limpiar.csv', index=False, sep=',')


if __name__ == '__main__':
    nombre_buscar = 'Alejandro Garcia'
    user = 'hugo.s251615@cesurformacion.com'
    passw = 'madrid46'
    chrome_driver = r'C:\Users\Hugo\Desktop\Nueva carpeta\chromedriver'
    extraer_datos(chrome_driver, user, passw, nombre_buscar)