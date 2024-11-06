# Reiko - Discord Bot for Advanced Administration & Fun

**Reiko** is a specialized Discord bot with powerful moderation, role management, announcement, and analytics features designed to enhance server management and engagement. This bot combines advanced admin tools with interactive features, helping both admins and members enjoy a well-managed and fun Discord experience.

> **Note**: Reiko is a private, custom bot project and is not intended for replication or cloning. Please respect the creator's work and refrain from duplicating the bot.

---

## 🌟 Features & Commands Guide

### ⚙️ Moderation Commands
- **`/warn @user [reason]`**: Warns a user and tracks their warning count.
  - Example: `/warn @user Spamming in chat`

- **`/tempban @user [duration] [reason]`**: Temporarily bans a user for a specified time (in minutes).
  - Example: `/tempban @user 60 Excessive toxicity`

- **`/tempmute @user [duration] [reason]`**: Temporarily mutes a user for a specified time (in minutes).
  - Example: `/tempmute @user 30 Spam`

### 🛡️ Role Management
- **`/createreactionrole [title] [description] [#channel]`**: Creates a reaction role message for role assignment.
  - Example: `/createreactionrole "Get Roles" "React to get roles!" #roles`

- **`/addrole [message_id] [@role] [emoji]`**: Adds a role to a reaction role message, allowing members to react to obtain roles.
  - Example: `/addrole 123456789 @Gamer 🎮`

### 📢 Announcements
- **`/announce [#channel] [title] [content] [color] [@role]`**: Posts an immediate announcement in the specified channel.
  - Example: `/announce #announcements "Server Update" "New features added!" blue @everyone`

- **`/schedule [#channel] [title] [content] [time] [repeat]`**: Schedules announcements with repeat options (daily, weekly, monthly).
  - Example: `/schedule #events "Game Night" "Time to play!" "2024-03-20 20:00" weekly`

- **`/template [name] [title] [content]`**: Saves a customizable announcement template for later use.
  - Example: `/template gamenight "Game Night!" "It's time for games! 🎮"`

- **`/usetemplate [template_name] [#channel]`**: Posts an announcement using a saved template.
  - Example: `/usetemplate gamenight #announcements`

### 🎉 Welcome System
- **`/setwelcome [#channel] [message] [dm_message] [embed]`**: Configures welcome messages with placeholders (e.g., `{user}`, `{server}`, `{count}`).
  - Example: `/setwelcome #welcome "Welcome {user} to {server}!" "Thanks for joining!" true`

- **`/testwelcome`**: Tests the current welcome message setup.

### 📊 Analytics
- **`/serverstats [timeframe]`**: Displays server statistics over a specific timeframe (day, week, month).
  - Example: `/serverstats week`

- **`/userstats @user`**: Shows detailed statistics for a specific user.
  - Example: `/userstats @user`

- **`/channelstats [#channel]`**: Provides statistics for a specific channel.
  - Example: `/channelstats #general`

### 🔧 Custom Commands
- **`/createcmd [command_name] [response] [description]`**: Allows admins to create custom commands.
  - Example: `/createcmd rules "Server rules: 1. Be respectful" "Shows server rules"`

- **`/deletecmd [command_name]`**: Deletes a custom command.
  - Example: `/deletecmd rules`

- **`/listcmds`**: Lists all custom commands created in the server.

### 🚨 User Management
- **`/raidmode [enabled]`**: Toggles raid protection mode for enhanced security.
  - Example: `/raidmode true`

---

## 🛠️ Required Permissions

Reiko requires specific permissions to perform certain actions:
- **Moderation Commands**: `MODERATE_MEMBERS`
- **Role Commands**: `MANAGE_ROLES`
- **Announcements**: `MANAGE_MESSAGES`
- **Welcome Setup**: `MANAGE_GUILD`
- **Analytics**: `VIEW_AUDIT_LOG`

---

## 🚀 Getting Started

To use **Reiko** effectively, make sure it has the required permissions and use the command prefix `/`. Reiko’s settings and configurations are automatically saved, so any changes made are applied immediately.

### Command Structure
- **Slash Commands**: Reiko uses Discord’s slash command system for ease and compatibility.
- **Required Parameters**: Parameters shown in `[brackets]` are required for the command.
- **Optional Parameters**: Parameters not in brackets are optional and can be customized as needed.

---

## 🔒 Privacy & Non-Replication Notice

This bot is a personal project and is **not intended for cloning or replication**. Please respect the unique nature of Reiko and refrain from duplicating its functionality or features.

## 💬 Support

For questions or support with **Reiko**, please contact the bot's creator directly.

Thank you for your interest in **Reiko**! This bot was crafted with attention to detail to provide an enjoyable and efficient experience for both administrators and members.
