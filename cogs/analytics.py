import discord
from discord import app_commands
from discord.ext import commands
import json
import logging
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import io
from textblob import TextBlob
import pandas as pd
import seaborn as sns

logger = logging.getLogger('discord')

class Analytics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.analytics_data = defaultdict(lambda: {
            'message_count': defaultdict(int),
            'channel_activity': defaultdict(lambda: defaultdict(int)),
            'user_activity': defaultdict(lambda: defaultdict(int)),
            'keyword_tracking': defaultdict(int),
            'sentiment_data': [],
            'voice_activity': defaultdict(lambda: defaultdict(int)),
            'hourly_activity': defaultdict(lambda: defaultdict(int))
        })
        self.load_data()

    def load_data(self):
        try:
            with open('data/analytics.json', 'r') as f:
                data = json.load(f)
                # Convert the loaded data to our defaultdict structure
                for guild_id, guild_data in data.items():
                    for key, value in guild_data.items():
                        self.analytics_data[guild_id][key] = value
        except FileNotFoundError:
            self.save_data()

    def save_data(self):
        # Convert defaultdict to regular dict for JSON serialization
        data_to_save = {}
        for guild_id, guild_data in self.analytics_data.items():
            data_to_save[guild_id] = dict(guild_data)
        
        with open('data/analytics.json', 'w') as f:
            json.dump(data_to_save, f, indent=4)

    @app_commands.command(name="serverstats", description="View server statistics")
    @app_commands.default_permissions(view_audit_log=True)
    async def server_stats(
        self,
        interaction: discord.Interaction,
        timeframe: str = "week"  # day, week, month
    ):
        await interaction.response.defer()
        
        guild_id = str(interaction.guild_id)
        guild_data = self.analytics_data[guild_id]
        
        # Create visualization
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Channel Activity
        channel_data = pd.DataFrame.from_dict(guild_data['channel_activity'], orient='index')
        channel_data.plot(kind='bar', ax=ax1, title='Channel Activity')
        ax1.set_xlabel('Channels')
        ax1.set_ylabel('Messages')
        
        # Hourly Activity
        hourly_data = pd.DataFrame.from_dict(guild_data['hourly_activity'], orient='index')
        hourly_data.plot(kind='line', ax=ax2, title='Activity by Hour')
        ax2.set_xlabel('Hour')
        ax2.set_ylabel('Messages')
        
        # User Activity
        user_data = pd.DataFrame.from_dict(guild_data['user_activity'], orient='index')
        user_data.head(10).plot(kind='bar', ax=ax3, title='Top 10 Active Users')
        ax3.set_xlabel('Users')
        ax3.set_ylabel('Messages')
        
        # Sentiment Analysis
        sentiment_data = pd.DataFrame(guild_data['sentiment_data'])
        sns.histplot(data=sentiment_data, x='sentiment', ax=ax4, bins=20)
        ax4.set_title('Message Sentiment Distribution')
        
        # Save plot to buffer
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Create embed with summary
        embed = discord.Embed(
            title=f"Server Analytics - Past {timeframe}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        total_messages = sum(guild_data['message_count'].values())
        active_channels = len(guild_data['channel_activity'])
        active_users = len(guild_data['user_activity'])
        
        embed.add_field(name="Total Messages", value=str(total_messages))
        embed.add_field(name="Active Channels", value=str(active_channels))
        embed.add_field(name="Active Users", value=str(active_users))
        
        # Send response
        file = discord.File(buf, filename='stats.png')
        await interaction.followup.send(embed=embed, file=file)

    @app_commands.command(name="userstats", description="View statistics for a specific user")
    async def user_stats(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        guild_id = str(interaction.guild_id)
        user_id = str(user.id)
        guild_data = self.analytics_data[guild_id]
        
        embed = discord.Embed(
            title=f"User Analytics - {user.display_name}",
            color=user.color,
            timestamp=datetime.utcnow()
        )
        
        # Message count
        message_count = guild_data['user_activity'].get(user_id, {}).get('messages', 0)
        embed.add_field(name="Total Messages", value=str(message_count))
        
        # Activity hours
        active_hours = guild_data['user_activity'].get(user_id, {}).get('hours', {})
        peak_hour = max(active_hours.items(), key=lambda x: x[1])[0] if active_hours else "N/A"
        embed.add_field(name="Most Active Hour", value=peak_hour)
        
        # Voice activity
        voice_time = guild_data['voice_activity'].get(user_id, {}).get('total_minutes', 0)
        embed.add_field(name="Voice Channel Time", value=f"{voice_time} minutes")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="channelstats", description="View channel statistics")
    async def channel_stats(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None
    ):
        if channel is None:
            channel = interaction.channel
            
        guild_id = str(interaction.guild_id)
        channel_id = str(channel.id)
        guild_data = self.analytics_data[guild_id]
        
        # Create visualization of channel activity over time
        activity_data = guild_data['channel_activity'].get(channel_id, {})
        
        fig, ax = plt.subplots(figsize=(10, 5))
        pd.Series(activity_data).plot(kind='line', ax=ax)
        ax.set_title(f'Activity in #{channel.name}')
        ax.set_xlabel('Time')
        ax.set_ylabel('Messages')
        
        # Save plot to buffer
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Create embed with stats
        embed = discord.Embed(
            title=f"Channel Analytics - #{channel.name}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        total_messages = sum(activity_data.values())
        embed.add_field(name="Total Messages", value=str(total_messages))
        
        # Send response
        file = discord.File(buf, filename='channel_stats.png')
        await interaction.response.send_message(embed=embed, file=file)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
            
        guild_id = str(message.guild.id)
        channel_id = str(message.channel.id)
        user_id = str(message.author.id)
        hour = message.created_at.hour
        
        # Update message count
        self.analytics_data[guild_id]['message_count'][channel_id] += 1
        
        # Update channel activity
        self.analytics_data[guild_id]['channel_activity'][channel_id][message.created_at.strftime("%Y-%m-%d")] += 1
        
        # Update user activity
        self.analytics_data[guild_id]['user_activity'][user_id]['messages'] = \
            self.analytics_data[guild_id]['user_activity'][user_id].get('messages', 0) + 1
        
        if 'hours' not in self.analytics_data[guild_id]['user_activity'][user_id]:
            self.analytics_data[guild_id]['user_activity'][user_id]['hours'] = {}
        self.analytics_data[guild_id]['user_activity'][user_id]['hours'][hour] = \
            self.analytics_data[guild_id]['user_activity'][user_id]['hours'].get(hour, 0) + 1
        
        # Update hourly activity
        self.analytics_data[guild_id]['hourly_activity'][hour][message.created_at.strftime("%Y-%m-%d")] += 1
        
        # Keyword tracking
        words = message.content.lower().split()
        for word in words:
            self.analytics_data[guild_id]['keyword_tracking'][word] += 1
        
        # Sentiment analysis
        try:
            blob = TextBlob(message.content)
            sentiment = blob.sentiment.polarity
            self.analytics_data[guild_id]['sentiment_data'].append({
                'timestamp': message.created_at.isoformat(),
                'sentiment': sentiment
            })
        except:
            pass
        
        # Save periodically (you might want to optimize this)
        self.save_data()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild_id = str(member.guild.id)
        user_id = str(member.id)
        
        if before.channel != after.channel:
            if after.channel:
                # User joined a voice channel
                self.analytics_data[guild_id]['voice_activity'][user_id]['join_time'] = datetime.utcnow()
            elif before.channel:
                # User left a voice channel
                join_time = self.analytics_data[guild_id]['voice_activity'][user_id].get('join_time')
                if join_time:
                    duration = (datetime.utcnow() - join_time).total_seconds() / 60
                    self.analytics_data[guild_id]['voice_activity'][user_id]['total_minutes'] = \
                        self.analytics_data[guild_id]['voice_activity'][user_id].get('total_minutes', 0) + duration
                    self.save_data()

async def setup(bot):
    await bot.add_cog(Analytics(bot)) 