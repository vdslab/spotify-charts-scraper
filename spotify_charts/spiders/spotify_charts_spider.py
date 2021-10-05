import scrapy

BASE_URL = 'https://spotifycharts.com/regional'


class SpotifyChartsSpider(scrapy.Spider):
    name = "spotify_charts"

    def start_requests(self):
        top_page_url = BASE_URL
        yield scrapy.Request(url=top_page_url, callback=self.parse_country)

    def parse_country(self, response):
        r = response
        countries = r.css(
            '#content > div > div > div > span > div.wrapper > div > div > div > div:nth-child(1) > ul > li::attr(data-value)').getall()

        for country in countries:
            latest_url = f'{BASE_URL}/{country}/weekly/latest'
            yield r.follow(latest_url, callback=self.parse_week)
            break

    def parse_week(self, response):
        r = response
        country = r.url.split('/')[4]
        weeks = r.css(
            '#content > div > div > div > span > div.wrapper > div > div > div > div:nth-child(3) > ul > li::attr(data-value)').getall()

        for week in weeks:
            url = f'{BASE_URL}/{country}/weekly/{week}'
            yield r.follow(url, callback=self.parse)
            break

    def parse(self, response):
        r = response
        url = r.url
        selected_values = r.css('div.responsive-select-value::text').getall()

        musics = []

        tb = r.css('#content > div > div > div > span > table > tbody > tr')
        for tr in tb:
            id = tr.css(
                'td.chart-table-image > a::attr(href)').get().split('/')[-1]
            ranking = tr.css('td.chart-table-position::text').get()
            title = tr.css('td.chart-table-track > strong::text').get()
            artist_or_album_names = tr.css(
                'td.chart-table-track > span::text').get()
            streams = tr.css('td.chart-table-streams::text').get()
            m = {
                'id': id,
                'ranking': ranking,
                'title': title,
                'artist_or_album_names': artist_or_album_names,
                'streams': streams
            }

            musics.append(m)

        yield {
            'url': url,
            'selected_values': selected_values,
            'musics': musics
        }
