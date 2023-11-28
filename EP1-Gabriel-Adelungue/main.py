import scrapy

## Gabriel Adelungue Cassiano


class PokeSpider(scrapy.Spider):
  name = "pokespider"
  start_urls = ["https://pokemondb.net/pokedex/all"]

  def parse(self, response):
    # Encontrar todos os links para as páginas de Pokémon
    pokemon_links = response.css(
        'table#pokedex > tbody > tr td:nth-child(2) > a::attr(href)').getall()

    # Iterar sobre os links e seguir para a página de cada Pokémon
    for link in pokemon_links:
      yield response.follow(link, self.parse_pokemon)

  def parse_pokemon(self, response):
    # Extrair informações básicas do Pokémon
    pokemon_data = {
        "Id":
        response.css(
            "table.vitals-table > tbody > tr:nth-child(1) > td > strong::text"
        ).get(),
        "Nome":
        response.css("main#main > h1::text").get(),
        "Altura":
        response.css(
            "table.vitals-table > tbody > tr:nth-child(4) > td::text").get(),
        "Peso":
        response.css(
            "table.vitals-table > tbody > tr:nth-child(5) > td::text").get(),
        "Tipos": [
            tipo.strip() for tipo in response.css(
                "table.vitals-table > tbody > tr:nth-child(2) > td a.type-icon::text"
            ).getall()
        ]
    }

    # Extrair informações de evolução
    evolutions = []
    evolution_cards = response.css(
        "div.infocard-list-evo > div.infocard:not(:first-child)")
    for evolution_card in evolution_cards:
      id_evolution = evolution_card.css('small::text').get()
      name_evolution = evolution_card.css('a.ent-name::text').get()
      url_evolution = evolution_card.css('a.ent-name::attr(href)').get()

      if id_evolution and name_evolution and url_evolution:
        evolutions.append({
            "Id": id_evolution,
            'Nome': name_evolution,
            'URL': url_evolution
        })

    # Extrair URLs das habilidades e seguir para cada uma
    ability_urls = response.css(
        'table.vitals-table > tbody > tr:nth-child(6) td a::attr(href)'
    ).getall()
    for ability_url in ability_urls:
      yield response.follow(ability_url,
                            self.parse_ability,
                            meta={
                                "pokemon_data": pokemon_data,
                                "Evolucoes": evolutions
                            })

  def parse_ability(self, response):
    # Extrair informações da habilidade
    ability_data = {
        "Nome":
        response.css("h1::text").get(),
        "URL":
        response.url,
        "Descricao":
        ' '.join(
            response.css(
                'div > div > h2:contains("Effect") + p::text').getall())
    }

    # Combinar informações do Pokémon com as da habilidade
    pokemon_data = response.meta["pokemon_data"]
    evolutions = response.meta["Evolucoes"]

    yield {
        "Id": pokemon_data["Id"],
        "URL": response.meta["pokemon_data"]["URL"],
        "Nome": pokemon_data["Nome"],
        "Altura": pokemon_data["Altura"],
        "Peso": pokemon_data["Peso"],
        "Tipos": pokemon_data["Tipos"],
        "Evolucoes": evolutions,
        "Habilidades": ability_data
    }
