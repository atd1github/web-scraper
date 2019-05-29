import re
import os
import csv
import requests
from bs4 import BeautifulSoup


def get_html_content(url):
    """
    get the html content of the url
    and parse it using BeautifulSoup
    """
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, features="html.parser")
    return soup


def get_dem(row):
    links = row.findAll('a')
    for link in links:
        # visit the link which starts from '/wiki'
        # and get the html content from city url
        # parse it using BeautifulSoup
        if link.attrs.get('href', '').startswith('/wiki'):
            city_url = 'https://en.wikipedia.org/{}'.format(link['href'])
            soup = get_html_content(city_url)
            
            for row in soup.findAll('tr'):
                if 'Demonym' in row.text:
                    for td in row.findAll('td'):
                        
                        # remove <sup> and <a> tag
                        for sup in td.find_all('sup'):
                            sup.unwrap()
                        for sup in td.find_all('a'):
                            sup.unwrap()
                        
                        # remove <br> and <td> tag
                        value = str(td)
                        if '<br/>' in value:
                            value = value.replace('<br/>', ' ')
                        value = value.replace('<td>', '')
                        value = value.replace('</td>', '')
                        
                        return value
            

def main():
    # get the html content from the url and parse it using BeautifulSoup
    url = 'https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population'
    soup = get_html_content(url)
    
    # find the table of cities from the html content
    table = soup.find('table', attrs={'class': 'wikitable sortable'})


    # creates the csv file in the same location where this python scripts exists
    # under the name of cities.csv
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cities.csv'), 'w') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(['Rank', 'City', 'State', '2018 Est.', '2010 Census', 'Demonym'])

        for idx1, row in enumerate(table.findAll('tr')):
            
            # ignoring first row
            if idx1 == 0:
                continue
            # end after 15 cities
            if idx1 > 15:
                break
            
            # get the Demonym value
            dem_value = get_dem(row)
            
            city_details = []
            cells = row.findAll('td')
            
            for idx2, cell in enumerate(cells):
                if idx2 < 5:
                    
                    cell_text = cell.text
                    # remove the square brackets and content inside it
                    start = cell_text.find('[')
                    end = cell_text.find(']')
                    if start != -1 and end != -1:
                        cell_text = '{}{}'.format(cell_text[0 : start], cell_text[end : len(cell_text)])
                    
                    # regex to just catch space and alpha numeric string
                    cell_text = re.findall(r'[a-zA-Z0-9\ ]*', cell_text)
                    value = "".join(string for string in cell_text if len(string) > 0)
                    
                    city_details.append(value)
                else:
                    break
                
            city_details.append(dem_value)
            wr.writerow(city_details)


# calls the main function
# gets the data of first 15 cities from the table in the url
# gets the Demonym value from each of the 15 cities url
if __name__ == '__main__':
    main()