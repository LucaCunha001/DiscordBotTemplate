import discord
import os
import psutil
import zipfile
from discord import app_commands
from datetime import datetime

def criar_zip(arquivos, nome_zip="meu_arquivo.zip"):
    with zipfile.ZipFile(nome_zip, 'w') as zipf:
        for arquivo in arquivos:
            if os.path.exists(arquivo):
                zipf.write(arquivo, os.path.basename(arquivo))
                print(f"Arquivo {arquivo} adicionado ao ZIP.")
            else:
                print(f"Arquivo {arquivo} não encontrado e foi ignorado.")
    print(f"Arquivo ZIP '{nome_zip}' criado com sucesso!")

arquivos_permitidos = ['bot.py', 'introducao.json', 'lv.py', 'requirements.txt', 'ups.json', 'warns.json', 'discloud.config', 'exp.json', 'cpu.py', 'embed.py']

class InfoCommands(app_commands.Group):
    def __init__(self, bot: discord.Client):
        super().__init__(name="info", description="Comandos de informações do bot")
        self.bot = bot
    
    @app_commands.command(name="status", description="Mostra o ping, memória utilizada, CPU e tamanho dos arquivos do bot")
    async def status(self, interaction: discord.Interaction):
        await interaction.response.defer()
        latency = round(self.bot.latency * 1000)
        process = psutil.Process(os.getpid())
        memory_used = process.memory_info().rss / 1024 / 1024
        cpu_percent = psutil.cpu_percent(interval=1)
        
        total_size = sum(
            os.path.getsize(os.path.join(dirpath, f))
            for dirpath, _, filenames in os.walk(".")
            for f in filenames if f in arquivos_permitidos
        )
        
        total_size_mb = total_size / 1024 / 1024
        embed = discord.Embed(
            title="Status do Bot",
            description="Aqui estão as informações de desempenho do bot:",
            colour=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Ping", value=f"`{latency} ms`", inline=True)
        embed.add_field(name="Memória Utilizada", value=f"`{memory_used:.2f} MB`", inline=True)
        embed.add_field(name="Uso de CPU", value=f"`{cpu_percent}%`", inline=True)
        embed.add_field(name="Peso dos Arquivos", value=f"`{total_size_mb:.2f} MB`", inline=True)
        embed.set_footer(text="Status do bot", icon_url=interaction.guild.icon.url if interaction.guild else None)
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild else None)

        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="discloud", description="Cria ou edita o arquivo discloud.config")
    @app_commands.describe(
        projeto="Nome do projeto no Discloud",
        linguagem="Linguagem do bot (ex: python, nodejs)",
        memoria="Quantidade de memória (em MB) necessária para o projeto"
    )
    async def configurar(self, interaction: discord.Interaction, projeto: str, linguagem: str, memoria: int):
        config_content=f"NAME={projeto}\nAVATAR={self.bot.user.avatar.url}\nTYPE=bot\nMAIN=main.py\nRAM={memoria}\nAUTORESTART=true\nVERSION=latest\nAPT=tools"
        requirements = "discord.py\npsutil"

        with open("discloud.config", "w") as config_file:
            config_file.write(config_content)
        with open("requirements.txt", "w") as requirements_file:
            requirements_file.write(requirements)
        embed = discord.Embed(
            title="Configuração do Discloud",
            description="O arquivo `discloud.config` foi configurado com sucesso.",
            color=discord.Color.green()
        )

        embed.set_footer(text="RDA - Rede de Amizade", icon_url=interaction.guild.icon.url if interaction.guild else None)
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild else None)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.add_field(name="Projeto", value=projeto, inline=True)
        embed.add_field(name="Linguagem", value=linguagem, inline=True)
        embed.add_field(name="Memória", value=f"{memoria} MB", inline=True)
        embed.set_footer(text="Arquivo criado no diretório do bot.")

        await interaction.response.send_message(embed=embed, ephemeral=True)
    @app_commands.command(name="arquivo_discloud", description="Mostra o arquivo ZIP para upar na Discloud")
    async def discloudzip(self, interaction: discord.Interaction):
        criar_zip(arquivos_permitidos, "discloud.zip")
        arquivo_zip = discord.File("discloud.zip")
        await interaction.response.send_message(file=arquivo_zip, ephemeral=True)
        os.remove("discloud.zip")