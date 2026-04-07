"""
SafeScroll Medium Difficulty Scenarios — Context-Dependent Content Moderation

These 10 scenarios are designed to teach AI agents contextual judgment in content
moderation. The core principle: identical or near-identical content can be safe in
one context but harmful in another. Scenarios are organized in pairs where the
content is similar but the correct moderation decision differs based on surrounding
context such as community, audience age, platform feature (public vs DM), poster
credentials, and relationship between users.

Pairs:
    1-2: Aggressive / threatening language (gaming trash talk vs unsolicited DM to minor)
    3-4: Dark humor / morbid expressions (comedy group vs memorial post)
    5-6: Anatomical / medical content (health education vs kids community)
    7-8: Adult-to-minor private messages (verified teacher vs unknown adult)
    9:   Standalone — bait-and-switch content pattern targeting teens
   10:   Standalone — heated political rhetoric
"""

MEDIUM_SCENARIOS = [
    # =========================================================================
    # PAIR 1 — Aggressive Language
    # =========================================================================
    {
        "scenario_id": "medium_001",
        "content_text": (
            "I'm going to absolutely DESTROY you tonight. You won't stand a chance. "
            "Prepare to get wrecked!! No mercy this time. GG in advance 😤🎮🔥"
        ),
        "content_type": "comment",
        "platform": "instagram",
        "community_context": "gaming",
        "poster_profile": {
            "username": "FragMaster_Kai",
            "age": 19,
            "account_age_days": 730,
            "followers": 5400,
            "following": 620,
            "posts": 347,
            "verified": False,
            "bio": "Twitch Affiliate | Apex & Valorant | Ranked Grinder | DM for scrims 🎯",
        },
        "target_user_profile": {
            "username": "ClutchDemonJay",
            "age": 21,
            "account_age_days": 1095,
            "followers": 8200,
            "following": 410,
            "posts": 512,
            "verified": False,
            "bio": "FPS addict | Kai's rival since Season 3 | Content Creator",
        },
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "Automated detection of threatening language: 'destroy you', 'no mercy', 'get wrecked'",
            "reports_count": 0,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "approve",
            "severity": "none",
            "category": "safe",
            "account_action": "none",
            "escalate_to": "none",
            "critical_context_factors": [
                "gaming_context",
                "competitive_trash_talk",
                "established_rivalry",
                "both_adults",
                "public_comment_not_dm",
                "gaming_emoji_and_slang",
                "mutual_community_participation",
            ],
        },
    },
    {
        "scenario_id": "medium_002",
        "content_text": (
            "I'm going to absolutely DESTROY you tonight. You won't stand a chance. "
            "No mercy this time."
        ),
        "content_type": "dm",
        "platform": "instagram",
        "community_context": "general",
        "poster_profile": {
            "username": "darknight_032",
            "age": 28,
            "account_age_days": 90,
            "followers": 34,
            "following": 487,
            "posts": 6,
            "verified": False,
            "bio": "",
        },
        "target_user_profile": {
            "username": "emily_sophiaa",
            "age": 16,
            "is_minor": True,
            "account_age_days": 540,
            "followers": 312,
            "following": 275,
            "posts": 89,
            "verified": False,
            "bio": "Sophomore 💛 | Volleyball #12 | she/her",
        },
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "Automated detection of threatening language in DM to minor: 'destroy you', 'no mercy'",
            "reports_count": 0,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "flag_review",
            "severity": "high",
            "category": "harassment",
            "account_action": "restrict",
            "escalate_to": "human_review",
            "critical_context_factors": [
                "dm_not_public",
                "no_prior_relationship",
                "target_is_minor",
                "age_gap",
                "no_mutual_connections",
                "threatening_language_in_private",
                "new_account_low_activity",
                "high_following_to_follower_ratio",
            ],
        },
    },
    # =========================================================================
    # PAIR 2 — Dark Humor / Morbid Language
    # =========================================================================
    {
        "scenario_id": "medium_003",
        "content_text": (
            "I swear this Monday is trying to kill me. If this meeting doesn't end "
            "soon, I'm going to lose it. Someone put me out of my misery already "
            "😩💀 #MondayMood #CorporateLife #EndMe"
        ),
        "content_type": "group_post",
        "platform": "facebook",
        "community_context": "comedy",
        "poster_profile": {
            "username": "PriyaMehta",
            "age": 27,
            "account_age_days": 1825,
            "followers": 1340,
            "following": 890,
            "posts": 203,
            "verified": False,
            "bio": "Marketing Manager by day, meme connoisseur by night. Sarcasm is my love language.",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "Automated detection of self-harm language: 'kill me', 'put me out of my misery', 'end me'",
            "reports_count": 0,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "approve",
            "severity": "none",
            "category": "safe",
            "account_action": "none",
            "escalate_to": "none",
            "critical_context_factors": [
                "comedy_context",
                "hyperbolic_language",
                "common_expression",
                "established_account",
                "emoji_indicates_humor",
                "humor_hashtags",
                "workplace_humor_genre",
                "no_genuine_distress_indicators",
            ],
        },
    },
    {
        "scenario_id": "medium_004",
        "content_text": (
            "Ugh just kill me already, this is so boring. Put me out of my misery lol. "
            "Can this be over yet 💀😴"
        ),
        "content_type": "comment",
        "platform": "facebook",
        "community_context": "general",
        "poster_profile": {
            "username": "TrollerX99",
            "age": None,
            "account_age_days": 15,
            "followers": 8,
            "following": 56,
            "posts": 4,
            "verified": False,
            "bio": "just vibing",
        },
        "target_user_profile": {
            "username": "RamirezFamily_Official",
            "age": 44,
            "account_age_days": 2190,
            "followers": 620,
            "following": 305,
            "posts": 78,
            "verified": False,
            "bio": "Celebrating the life of our beloved Daniel ❤️ 1998-2025. Forever in our hearts.",
        },
        "reporter_info": {
            "type": "user_reported",
            "reason": "Disrespectful and insensitive comment on our memorial post for my brother. This person does not know our family.",
            "reports_count": 4,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "remove",
            "severity": "medium",
            "category": "harassment",
            "account_action": "warn",
            "escalate_to": "none",
            "critical_context_factors": [
                "memorial_context",
                "insensitive_to_grief",
                "targeting_grieving_family",
                "disrespectful_timing",
                "no_connection_to_family",
                "new_account",
                "multiple_user_reports",
                "trivializing_death_on_tribute_post",
            ],
        },
    },
    # =========================================================================
    # PAIR 3 — Body / Medical Content
    # =========================================================================
    {
        "scenario_id": "medium_005",
        "content_text": (
            "Monthly reminder for all my fellow healthcare professionals: here's "
            "the correct technique for clinical breast examination (CBE). Step 1: "
            "Patient should be supine with ipsilateral arm raised. Using the pads "
            "of your three middle fingers, apply light, medium, and deep pressure "
            "in concentric circles starting from the outer breast tissue moving "
            "toward the nipple. Palpate all four quadrants and the axillary tail. "
            "Document any masses noting size, shape, mobility, and tenderness. "
            "Early detection saves lives — share this with your nursing students! "
            "#NurseEducation #WomensHealth #BreastCancerAwareness #CBE"
        ),
        "content_type": "post",
        "platform": "facebook",
        "community_context": "education",
        "poster_profile": {
            "username": "NurseJackie_RN",
            "age": 38,
            "account_age_days": 1095,
            "followers": 14500,
            "following": 820,
            "posts": 487,
            "verified": True,
            "bio": "BSN, RN | Women's Health Educator | 12 yrs clinical experience | Adjunct Faculty — Metro College of Nursing",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "Automated detection of explicit anatomical terminology: 'breast', 'nipple', 'palpate'",
            "reports_count": 0,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "approve",
            "severity": "none",
            "category": "safe",
            "account_action": "none",
            "escalate_to": "none",
            "critical_context_factors": [
                "educational_context",
                "medical_professional",
                "health_information",
                "appropriate_audience",
                "verified_account",
                "clinical_tone",
                "healthcare_hashtags",
                "established_account_with_history",
                "nursing_education_purpose",
            ],
        },
    },
    {
        "scenario_id": "medium_006",
        "content_text": (
            "Hey girls!! 💕 So I want to talk about breast development and what's "
            "normal. Let me describe what different stages look like and how to "
            "examine yourself. Your nipples might look different and that's okay. "
            "I'll explain what to touch and feel for... DM me for more personal "
            "guidance!! #TeenGirls #Puberty #BodyTalk #GirlTalk #Teen #Growing"
        ),
        "content_type": "post",
        "platform": "instagram",
        "community_context": "kids",
        "poster_profile": {
            "username": "body.wellness.guru",
            "age": None,
            "account_age_days": 22,
            "followers": 78,
            "following": 1240,
            "posts": 9,
            "verified": False,
            "bio": "wellness tips 🌿 body positivity ✨ DM always open",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "Anatomical content flagged in youth-targeted post. Hashtags targeting minors detected.",
            "reports_count": 2,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "remove",
            "severity": "medium",
            "category": "explicit_adult",
            "account_action": "restrict",
            "escalate_to": "human_review",
            "critical_context_factors": [
                "kids_community",
                "no_medical_credentials",
                "targeting_minors",
                "age_inappropriate_content",
                "suspicious_hashtags",
                "soliciting_dms_from_minors",
                "new_account_low_credibility",
                "high_following_to_follower_ratio",
                "vague_bio_no_qualifications",
            ],
        },
    },
    # =========================================================================
    # PAIR 4 — Adult-to-Minor Communication
    # =========================================================================
    {
        "scenario_id": "medium_007",
        "content_text": (
            "Hi Sarah, just a quick reminder — the science fair project proposal "
            "is due tomorrow by 3pm. The rubric and grading criteria are posted on "
            "Google Classroom under the Week 12 module. Let me know if you have "
            "any questions. You can also ask during office hours tomorrow morning. "
            "Good luck! — Ms. Patel"
        ),
        "content_type": "dm",
        "platform": "instagram",
        "community_context": "education",
        "poster_profile": {
            "username": "ms.patel_science",
            "age": 34,
            "account_age_days": 1460,
            "followers": 890,
            "following": 340,
            "posts": 156,
            "verified": True,
            "bio": "Science Teacher @ Lincoln High School | AP Bio & Chemistry | National Board Certified | she/her",
        },
        "target_user_profile": {
            "username": "sarah_bakes_stuff",
            "age": 15,
            "is_minor": True,
            "account_age_days": 365,
            "followers": 210,
            "following": 195,
            "posts": 47,
            "verified": False,
            "bio": "LHS Class of '28 🎓 | Baking & science nerd 🧪🧁",
        },
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "Adult-to-minor DM detected. Automated review triggered by age differential.",
            "reports_count": 0,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "approve",
            "severity": "none",
            "category": "safe",
            "account_action": "none",
            "escalate_to": "none",
            "critical_context_factors": [
                "verified_teacher",
                "school_context",
                "homework_topic",
                "mutual_connections_with_school",
                "professional_tone",
                "parent_visible_account",
                "references_official_platform",
                "signed_with_professional_name",
                "established_account",
                "no_personal_questions",
            ],
        },
    },
    {
        "scenario_id": "medium_008",
        "content_text": (
            "Hey! 😊 I noticed you're really into science — your project posts are "
            "super impressive for your age! I actually used to be a science teacher "
            "before I moved. I could totally help you with homework or projects if "
            "you want? I have tons of resources. What school do you go to? Maybe "
            "we could meet at a library or something to go over stuff. No pressure!"
        ),
        "content_type": "dm",
        "platform": "instagram",
        "community_context": "general",
        "poster_profile": {
            "username": "mike_scienceguy",
            "age": 32,
            "account_age_days": 20,
            "followers": 17,
            "following": 345,
            "posts": 3,
            "verified": False,
            "bio": "Science enthusiast 🔬 love helping students learn!",
        },
        "target_user_profile": {
            "username": "curious.katie.14",
            "age": 14,
            "is_minor": True,
            "account_age_days": 280,
            "followers": 155,
            "following": 180,
            "posts": 32,
            "verified": False,
            "bio": "8th grade 🏫 | future marine biologist 🐠 | she/her",
        },
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "Adult-to-minor unsolicited DM. Account follows 300+ minor accounts. Asking for personal information.",
            "reports_count": 0,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "flag_review",
            "severity": "high",
            "category": "grooming",
            "account_action": "suspend",
            "escalate_to": "child_safety_team",
            "critical_context_factors": [
                "unknown_adult",
                "no_established_relationship",
                "asking_personal_info",
                "new_account",
                "follows_many_minors",
                "unsolicited_dm_to_minor",
                "suggesting_offline_meeting",
                "flattery_and_compliments",
                "unverifiable_credentials",
                "isolating_language",
            ],
        },
    },
    # =========================================================================
    # STANDALONE CASE 9 — Bait-and-Switch Content Pattern
    # =========================================================================
    {
        "scenario_id": "medium_009",
        "content_text": (
            "Wait for it... 😏🔥 Trust me, the ending will SHOCK you! You are NOT "
            "ready for this 👀💦 Don't scroll past, I promise it's worth it!! "
            "#teens #viral #surprise #trending #foryou #fyp #waitforit #shocking"
        ),
        "content_type": "reel_description",
        "platform": "instagram",
        "community_context": "general",
        "poster_profile": {
            "username": "viral.clips.daily",
            "age": None,
            "account_age_days": 5,
            "followers": 42,
            "following": 12,
            "posts": 3,
            "verified": False,
            "bio": "The craziest clips you'll ever see 🤯🔞 Link in bio for more!",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "New account with bait-and-switch content pattern detected. All 3 posts use identical engagement-bait format. Hashtags targeting minors combined with suggestive emoji.",
            "reports_count": 3,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "flag_review",
            "severity": "medium",
            "category": "explicit_adult",
            "account_action": "restrict",
            "escalate_to": "human_review",
            "critical_context_factors": [
                "bait_and_switch_pattern",
                "targeting_teen_hashtags",
                "new_account",
                "clickbait_pattern",
                "repeated_behavior",
                "minor_targeting",
                "suggestive_emoji_combination",
                "age_restricted_emoji_in_bio",
                "no_age_disclosed",
                "multiple_user_reports",
            ],
        },
    },
    # =========================================================================
    # STANDALONE CASE 10 — Heated Political Rhetoric
    # =========================================================================
    {
        "scenario_id": "medium_010",
        "content_text": (
            "You people are absolutely INSANE if you think this policy works. Every "
            "single one of you supporting this is destroying our country. Wake up, "
            "you brainwashed sheep!! This is what happens when you refuse to look at "
            "the actual data. I've been saying this for YEARS and nobody listens. "
            "Open your eyes before it's too late."
        ),
        "content_type": "comment",
        "platform": "facebook",
        "community_context": "news",
        "poster_profile": {
            "username": "RobertChen_Writes",
            "age": 51,
            "account_age_days": 1825,
            "followers": 2300,
            "following": 670,
            "posts": 1045,
            "verified": False,
            "bio": "Independent political commentator | Data analyst | Opinions are my own. Let's debate, not cancel.",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "user_reported",
            "reason": "Hateful and aggressive comment. Calling people insane and sheep is harassment.",
            "reports_count": 6,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "approve",
            "severity": "none",
            "category": "safe",
            "account_action": "none",
            "escalate_to": "none",
            "critical_context_factors": [
                "political_discourse",
                "strong_opinion_not_hate",
                "no_protected_group_targeted",
                "established_account",
                "debate_context",
                "no_personal_threats",
                "hyperbolic_language",
                "news_community_expects_debate",
                "criticizing_policy_not_identity",
                "no_incitement_to_violence",
            ],
        },
    },
]
