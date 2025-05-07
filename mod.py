import datetime
import discord
import json
import os
from discord import app_commands
from typing import Callable, Optional

class Moderação(app_commands.Group):
    def __init__(self, bot, constantes, enviar_log):
        super().__init__(description="Comandos de moderação")
        self.bot: discord.Client = bot
        self.constantes = constantes
        self.enviar_log: Callable[
            [str, str, discord.Member, Optional[discord.File], Optional[int]]
        ] = enviar_log
        
    @app_commands.command(name="ban", description="Bane um membro")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, membro: discord.User, motivo: str = "Nenhuma razão fornecida"):
        embed = discord.Embed(
            title="Sucesso!",
            description=f"{membro.mention} foi banido.",
            colour=discord.Color.green()
        )
        embed.add_field(name="Motivo:", value=motivo)
        embed.add_field(name="Banido por:", value=interaction.user.mention)
        embed.set_thumbnail(url=membro.avatar.url if membro.avatar else membro.default_avatar.url)
        if membro.id == interaction.user.id:
            await interaction.response.send_message("Você não pode banir a si mesmo!", ephemeral=True)
            return

        if membro in interaction.guild.members:
            membro: discord.Member = membro
            if membro.top_role >= interaction.user.top_role:
                await interaction.response.send_message("Você não pode banir alguém com um cargo igual ou superior ao seu!", ephemeral=True)
                return

        if not interaction.guild.me.guild_permissions.ban_members:
            await interaction.response.send_message("Eu não tenho permissão para banir membros!", ephemeral=True)
            return

        try:
            await interaction.guild.ban(discord.Object(id=membro.id), reason=motivo)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Erro ao tentar banir {membro.mention}: {str(e)}", ephemeral=True)

    @app_commands.command(name="kick", description="Expulsa um membro do servidor")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, membro: discord.User, motivo: str = "Nenhuma razão fornecida"):
        embed = discord.Embed(
            title="Sucesso!",
            description=f"{membro.mention} foi expulso.",
            colour=discord.Color.orange()
        )
        embed.add_field(name="Motivo:", value=motivo)
        embed.add_field(name="Expulso por:", value=interaction.user.mention)
        embed.set_thumbnail(url=membro.avatar.url if membro.avatar else membro.default_avatar.url)

        if membro.id == interaction.user.id:
            await interaction.response.send_message("Você não pode expulsar a si mesmo!", ephemeral=True)
            return

        if membro in interaction.guild.members:
            if membro.top_role >= interaction.user.top_role:
                await interaction.response.send_message("Você não pode expulsar alguém com um cargo igual ou superior ao seu!", ephemeral=True)
                return

        if not interaction.guild.me.guild_permissions.kick_members:
            await interaction.response.send_message("Eu não tenho permissão para expulsar membros!", ephemeral=True)
            return

        try:
            await interaction.guild.kick(discord.Object(id=membro.id), reason=motivo)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Erro ao tentar expulsar {membro.mention}: {str(e)}", ephemeral=True)

    @app_commands.command(name="mute", description="Coloca um membro em timeout (silencia).")
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.describe(membro="O membro a ser silenciado.", duração="A duração do mute.", motivo="O motivo do mute.")
    @app_commands.choices(
        duration_units=[
            app_commands.Choice(name="Segundos", value="seconds"),
            app_commands.Choice(name="Minutos", value="minutes"),
            app_commands.Choice(name="Horas", value="hours"),
            app_commands.Choice(name="Dias", value="days")
        ]
    )
    async def mute(self, interaction: discord.Interaction, membro: discord.Member, duração: int, motivo: str = "Nenhuma razão fornecida", duration_units: str = "minutes"):
        if membro.id == interaction.user.id:
            await interaction.response.send_message("Você não pode colocar a si mesmo em timeout!", ephemeral=True)
            return

        if membro.top_role >= interaction.user.top_role:
            await interaction.response.send_message("Você não pode colocar em timeout alguém com um cargo igual ou superior ao seu!", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.moderate_members:
            await interaction.response.send_message("Eu não tenho permissão para moderar membros!", ephemeral=True)
            return

        unit_mapping = {
            "seconds": datetime.timedelta(seconds=duração),
            "minutes": datetime.timedelta(minutes=duração),
            "hours": datetime.timedelta(hours=duração),
            "days": datetime.timedelta(days=duração)
        }
        try:
            await membro.timeout(unit_mapping[duration_units], reason=motivo)
            await interaction.response.send_message(
                f"{membro.mention} foi colocado em timeout por {duração} {duration_units}. Motivo: {motivo}"
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Erro ao tentar colocar {membro.mention} em timeout: {str(e)}", ephemeral=True
            )

    @app_commands.command(name="unmute", description="Desmuta um membro")
    @app_commands.default_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, membro: discord.Member):
        if membro.id == interaction.user.id:
            await interaction.response.send_message("Você não pode desmutar a si mesmo!", ephemeral=True)
            return

        if membro.top_role >= interaction.user.top_role:
            await interaction.response.send_message("Você não pode desmutar alguém com um cargo igual ou superior ao seu!", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.moderate_members:
            await interaction.response.send_message("Eu não tenho permissão para desmutar membros!", ephemeral=True)
            return

        try:
            await membro.timeout(None, reason="Desmute")
            await interaction.response.send_message(f"{membro.mention} foi desmutado com sucesso.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Erro ao tentar desmutar {membro.mention}: {str(e)}", ephemeral=True)

    @app_commands.command(name="unban", description="Desbane um membro")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, membro: discord.User, motivo: str=None):
        if membro.id == interaction.user.id:
            await interaction.response.send_message("Você não pode desbanir a si mesmo!", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.ban_members:
            await interaction.response.send_message("Eu não tenho permissão para desbanir membros!", ephemeral=True)
            return

        try:
            await interaction.guild.unban(membro, reason=motivo)
            
            embed = discord.Embed(
                title="Sucesso!",
                description=f"{membro.mention} foi desbanido.",
                colour=discord.Color.green()
            )
            embed.add_field(name="Desbanido por:", value=interaction.user.mention)
            embed.set_thumbnail(url=membro.avatar.url if membro.avatar else membro.default_avatar.url)
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Erro ao tentar desbanir {membro.mention}: {str(e)}", ephemeral=True)

    WARN_FILE = "warns.json"

    def carregar_warns(self):
        if not os.path.exists(self.WARN_FILE):
            return {}
        try:
            with open(self.WARN_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}

    def salvar_warns(self, warns):
        with open(self.WARN_FILE, "w", encoding="utf-8") as file:
            json.dump(warns, file, indent=4, ensure_ascii=False)

    @app_commands.command(name="warn", description="Adiciona um aviso a um membro")
    @app_commands.default_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, membro: discord.Member, motivo: str = "Nenhuma razão fornecida"):
        if membro == interaction.user:
            return await interaction.response.send_message("Você não pode warnar a si mesmo!", ephemeral=True)
        if not interaction.user.top_role > membro.top_role:
            return await interaction.response.send_message("Você não pode warnar alguém com um cargo superior ao seu!!", ephemeral=True)
        warns = self.carregar_warns()
        if str(membro.id) not in warns:
            warns[str(membro.id)] = []
        if len(warns[str(membro.id)]) >= 6:
            await interaction.response.send_message(f"{membro.mention} já atingiu o limite de 6 avisos e será banido!", ephemeral=True)
            await membro.ban(reason="Atingiu o limite de 6 avisos")
            return

        novo_avisos = {
            "avisado_por": interaction.user.mention,
            "motivo": motivo,
            "data": datetime.datetime.now().isoformat()
        }
        warns[str(membro.id)].append(novo_avisos)
        self.salvar_warns(warns)

        embed = discord.Embed(
            title="MEMBRO AVISADO",
            colour=discord.Color.red()
        )
        embed.add_field(name="Membro:", value=membro.mention)
        embed.add_field(name="ID:", value=membro.id)
        embed.add_field(name="Avisado por:", value=interaction.user.mention)
        embed.add_field(name="Motivo:", value=motivo)
        embed.add_field(name="Avisos do membro:", value=f"`{len(warns[str(membro.id)])}/6`")
        embed.set_thumbnail(url=membro.avatar.url if membro.avatar else membro.default_avatar.url)

        mutar = [
            datetime.timedelta(hours=1),
            datetime.timedelta(hours=12),
            datetime.timedelta(days=1),
            datetime.timedelta(days=2),
            datetime.timedelta(days=7)
        ]
        try:
            await membro.timeout(mutar[len(warns[str(membro.id)])-1], reason=motivo)
        except Exception as e:
            print(f"Erro ao tentar colocar {membro.mention} em timeout: {str(e)}")

        await interaction.response.send_message(embed=embed)
        await self.enviar_log(tipo="Membro avisado", descrição=f"O membro {membro.mention} foi avisado por {interaction.user.mention}. Este é o `{len(warns[str(membro.id)])}º` aviso dele. Mais {6-len(warns[str(membro.id)])} e ele é banido.", por=interaction.user)
        canal = self.bot.get_channel(self.constantes.LOGS.LOG_PUNICOES)
        await canal.send(embed=embed)
        try:
            await membro.send(embed=embed)
        except Exception as e:
            del e
            pass

    @app_commands.command(name="warn_remove", description="Remove um aviso de um membro")
    @app_commands.default_permissions(moderate_members=True)
    async def warn_remove(self, interaction: discord.Interaction, membro: discord.Member, index: int):
        if membro == interaction.user:
            return await interaction.response.send_message("Você não pode remover um warn de si mesmo!", ephemeral=True)
        if not interaction.user.top_role > membro.top_role:
            return await interaction.response.send_message("Você não pode remover um warn de alguém com um cargo superior ao seu!!", ephemeral=True)
        warns = self.carregar_warns()

        if str(membro.id) not in warns or len(warns[str(membro.id)]) == 0:
            await interaction.response.send_message(f"{membro.mention} não tem nenhum warn registrado.", ephemeral=True)
            return

        if index < 1 or index > len(warns[str(membro.id)]):
            await interaction.response.send_message("Índice inválido! Use um valor entre 1 e o número de avisos.", ephemeral=True)
            return

        aviso_removido = warns[str(membro.id)].pop(index - 1)
        self.salvar_warns(warns)

        embed = discord.Embed(
            title="AVISO REMOVIDO",
            description=f"Aviso removido de {membro.mention}",
            colour=discord.Color.green()
        )
        embed.add_field(name="Membro:", value=membro.mention)
        embed.add_field(name="ID:", value=membro.id)
        embed.add_field(name="Aviso removido por:", value=interaction.user.mention)
        embed.add_field(name="Motivo:", value=aviso_removido["motivo"])
        embed.add_field(name="Avisos restantes:", value=f"{len(warns[str(membro.id)])}/6")
        
        await interaction.response.send_message(embed=embed)
        await self.enviar_log(tipo="Aviso removido", descrição=f"O membro {membro.mention} teve o {index}º aviso removido por {interaction.user.mention}. Sobrando `{len(warns[str(membro.id)])}` avisos.", por=interaction.user)
        canal = self.bot.get_channel(self.constantes.LOGS.LOG_PUNICOES)
        await canal.send(embed=embed)
        try:
            await membro.send(embed=embed)
        except Exception as e:
            del e
            pass

    @app_commands.command(name="warns", description="Verifica os warns de um membro.")
    async def warns(self, interaction: discord.Interaction, membro: discord.Member):
        warns = self.carregar_warns()

        if str(membro.id) not in warns or len(warns[str(membro.id)]) == 0:
            await interaction.response.send_message(f"{membro.mention} não tem nenhum warn registrado.", ephemeral=True)
            return

        warn_list = warns[str(membro.id)]
        warn_messages = "\n".join([f"{i+1}. {warn['motivo']}" for i, warn in enumerate(warn_list)])

        embed = discord.Embed(
            title=f"Warns de {membro.display_name}",
            description=f"**Membro:** {membro.mention}\n**ID:** {membro.id}\n\n**Avisos:**\n{warn_messages}",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)
