"""Default achievements data that matches the Flutter implementation"""

DEFAULT_ACHIEVEMENTS = [
    # First Task Achievements
    {
        "achievement_id": "first_task",
        "title": "Getting Started",
        "description": "Complete your first task",
        "icon_code_point": "0xe047",  # Icons.rocket_launch
        "color": "#4CAF50",  # Colors.green
        "type": "firstTask",
        "rarity": "common",
        "target_value": 1,
        "is_secret": False
    },

    # Task Milestone Achievements
    {
        "achievement_id": "task_master_10",
        "title": "Task Master",
        "description": "Complete 10 tasks",
        "icon_code_point": "0xe838",  # Icons.star
        "color": "#2196F3",  # Colors.blue
        "type": "taskMilestone",
        "rarity": "uncommon",
        "target_value": 10,
        "is_secret": False
    },
    {
        "achievement_id": "productivity_pro_50",
        "title": "Productivity Pro",
        "description": "Complete 50 tasks",
        "icon_code_point": "0xe3a5",  # Icons.diamond
        "color": "#9C27B0",  # Colors.purple
        "type": "taskMilestone",
        "rarity": "rare",
        "target_value": 50,
        "is_secret": False
    },
    {
        "achievement_id": "task_legend_100",
        "title": "Task Legend",
        "description": "Complete 100 tasks",
        "icon_code_point": "0xe3a6",  # Icons.emoji_events
        "color": "#FFC107",  # Colors.amber
        "type": "taskMilestone",
        "rarity": "epic",
        "target_value": 100,
        "is_secret": False
    },
    {
        "achievement_id": "task_god_500",
        "title": "Task God",
        "description": "Complete 500 tasks",
        "icon_code_point": "0xe570",  # Icons.military_tech
        "color": "#FF5722",  # Colors.deepOrange
        "type": "taskMilestone",
        "rarity": "legendary",
        "target_value": 500,
        "is_secret": False
    },

    # Streak Achievements
    {
        "achievement_id": "week_warrior",
        "title": "Week Warrior",
        "description": "Maintain a 7-day streak",
        "icon_code_point": "0xe515",  # Icons.local_fire_department
        "color": "#FF9800",  # Colors.orange
        "type": "streakMilestone",
        "rarity": "uncommon",
        "target_value": 7,
        "is_secret": False
    },
    {
        "achievement_id": "month_champion",
        "title": "Month Champion",
        "description": "Maintain a 30-day streak",
        "icon_code_point": "0xe3a6",  # Icons.emoji_events
        "color": "#FFC107",  # Colors.amber
        "type": "streakMilestone",
        "rarity": "rare",
        "target_value": 30,
        "is_secret": False
    },
    {
        "achievement_id": "streak_master_100",
        "title": "Streak Master",
        "description": "Maintain a 100-day streak",
        "icon_code_point": "0xe90e",  # Icons.whatshot
        "color": "#F44336",  # Colors.red
        "type": "streakMilestone",
        "rarity": "epic",
        "target_value": 100,
        "is_secret": False
    },
    {
        "achievement_id": "unstoppable_365",
        "title": "Unstoppable",
        "description": "Maintain a 365-day streak",
        "icon_code_point": "0xe3e8",  # Icons.flash_on
        "color": "#673AB7",  # Colors.deepPurple
        "type": "streakMilestone",
        "rarity": "legendary",
        "target_value": 365,
        "is_secret": False
    },

    # Consistency Achievements
    {
        "achievement_id": "consistent_performer",
        "title": "Consistent Performer",
        "description": "Complete tasks for 7 consecutive days",
        "icon_code_point": "0xe896",  # Icons.trending_up
        "color": "#4CAF50",  # Colors.green
        "type": "consistency",
        "rarity": "uncommon",
        "target_value": 7,
        "is_secret": False
    },
    {
        "achievement_id": "monthly_regular",
        "title": "Monthly Regular",
        "description": "Complete at least one task every day for 30 days",
        "icon_code_point": "0xe935",  # Icons.calendar_month
        "color": "#2196F3",  # Colors.blue
        "type": "consistency",
        "rarity": "rare",
        "target_value": 30,
        "is_secret": False
    },
    {
        "achievement_id": "habit_champion",
        "title": "Habit Champion",
        "description": "Maintain 80% consistency for 100 days",
        "icon_code_point": "0xe838",  # Icons.star
        "color": "#FF9800",  # Colors.orange
        "type": "consistency",
        "rarity": "epic",
        "target_value": 100,
        "is_secret": False
    },

    # Multi-tasking Achievements
    {
        "achievement_id": "multi_tasker",
        "title": "Multi-Tasker",
        "description": "Have 3 or more active streaks simultaneously",
        "icon_code_point": "0xe55c",  # Icons.multiple_stop
        "color": "#9C27B0",  # Colors.purple
        "type": "multiTasking",
        "rarity": "uncommon",
        "target_value": 3,
        "is_secret": False
    },
    {
        "achievement_id": "juggler",
        "title": "Juggler",
        "description": "Have 5 or more active streaks simultaneously",
        "icon_code_point": "0xe64e",  # Icons.psychology
        "color": "#3F51B5",  # Colors.indigo
        "type": "multiTasking",
        "rarity": "rare",
        "target_value": 5,
        "is_secret": False
    },

    # Health Integration Achievements
    {
        "achievement_id": "fitness_friend",
        "title": "Fitness Friend",
        "description": "Complete your first fitness-related task automatically",
        "icon_code_point": "0xe3f8",  # Icons.fitness_center
        "color": "#4CAF50",  # Colors.green
        "type": "healthIntegration",
        "rarity": "common",
        "target_value": 1,
        "is_secret": False
    },
    {
        "achievement_id": "health_hero",
        "title": "Health Hero",
        "description": "Complete 10 fitness tasks through health data sync",
        "icon_code_point": "0xe4bf",  # Icons.health_and_safety
        "color": "#8BC34A",  # Colors.lightGreen
        "type": "healthIntegration",
        "rarity": "uncommon",
        "target_value": 10,
        "is_secret": False
    },
    {
        "achievement_id": "wellness_warrior",
        "title": "Wellness Warrior",
        "description": "Complete 50 fitness tasks through health data sync",
        "icon_code_point": "0xe81f",  # Icons.self_improvement
        "color": "#009688",  # Colors.teal
        "type": "healthIntegration",
        "rarity": "rare",
        "target_value": 50,
        "is_secret": False
    },

    # Special Achievements
    {
        "achievement_id": "early_bird",
        "title": "Early Bird",
        "description": "Complete a task before 6 AM",
        "icon_code_point": "0xe91c",  # Icons.wb_sunny
        "color": "#FF9800",  # Colors.orange
        "type": "special",
        "rarity": "uncommon",
        "target_value": 1,
        "is_secret": True
    },
    {
        "achievement_id": "night_owl",
        "title": "Night Owl",
        "description": "Complete a task after 11 PM",
        "icon_code_point": "0xe5c9",  # Icons.nightlight_round
        "color": "#3F51B5",  # Colors.indigo
        "type": "special",
        "rarity": "uncommon",
        "target_value": 1,
        "is_secret": True
    },
    {
        "achievement_id": "weekend_warrior",
        "title": "Weekend Warrior",
        "description": "Complete tasks on both Saturday and Sunday",
        "icon_code_point": "0xe90f",  # Icons.weekend
        "color": "#00BCD4",  # Colors.cyan
        "type": "special",
        "rarity": "uncommon",
        "target_value": 1,
        "is_secret": False
    },
    {
        "achievement_id": "perfect_week",
        "title": "Perfect Week",
        "description": "Complete at least one task every day for a week",
        "icon_code_point": "0xe838",  # Icons.stars
        "color": "#FFC107",  # Colors.amber
        "type": "special",
        "rarity": "rare",
        "target_value": 1,
        "is_secret": False
    }
]


def get_achievement_by_id(achievement_id: str):
    """Get achievement data by ID"""
    return next((a for a in DEFAULT_ACHIEVEMENTS if a["achievement_id"] == achievement_id), None)


def get_achievements_by_type(achievement_type: str):
    """Get all achievements of a specific type"""
    return [a for a in DEFAULT_ACHIEVEMENTS if a["type"] == achievement_type]


def get_achievements_by_rarity(rarity: str):
    """Get all achievements of a specific rarity"""
    return [a for a in DEFAULT_ACHIEVEMENTS if a["rarity"] == rarity]
