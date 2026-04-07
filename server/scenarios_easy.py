"""
SafeScroll Easy Scenarios — 15 clear-cut content moderation cases.

Each scenario is unambiguous and has a single obviously correct decision.
These are used for introductory training and baseline evaluation of
content moderation agents. All scenarios require only 1 step (max_steps=1).
"""

EASY_SCENARIOS = [
    # ─────────────────────────────────────────────────────────────────────
    # 1. Follower-selling spam — Instagram fitness
    # ─────────────────────────────────────────────────────────────────────
    {
        "scenario_id": "easy_001",
        "content_text": (
            "Want 10K followers FAST? I gained 50,000 followers in just 2 days "
            "using this secret method! DM me for the link or visit my bio. "
            "100% real followers, guaranteed results, only $4.99!"
        ),
        "content_type": "comment",
        "platform": "instagram",
        "community_context": "fitness",
        "poster_profile": {
            "username": "follower_boost_2026",
            "age": None,
            "account_age_days": 2,
            "followers": 14,
            "following": 4800,
            "posts": 0,
            "verified": False,
            "bio": "Get REAL followers fast! DM for prices. #followersforlife #growyouraccount",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "spam_detection_pattern",
            "reports_count": 0,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "remove",
            "severity": "medium",
            "category": "spam",
            "account_action": "suspend",
            "escalate_to": "none",
            "critical_context_factors": [
                "brand_new_account",
                "zero_posts_high_following_ratio",
                "follower_selling_language",
                "monetary_solicitation",
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────────────
    # 2. Safe cooking post — false report from competitor
    # ─────────────────────────────────────────────────────────────────────
    {
        "scenario_id": "easy_002",
        "content_text": (
            "Just made my grandma's famous chicken tikka masala from scratch! "
            "The secret is toasting your spices in ghee before adding the tomato "
            "base. Took me 3 hours but totally worth it. Recipe in my highlights! "
            "#homecooking #tikkamasala"
        ),
        "content_type": "post",
        "platform": "instagram",
        "community_context": "general",
        "poster_profile": {
            "username": "priya_cooks_daily",
            "age": 31,
            "account_age_days": 1095,
            "followers": 12400,
            "following": 620,
            "posts": 287,
            "verified": False,
            "bio": "Home chef sharing family recipes from Punjab. New recipe every Tuesday!",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "user_reported",
            "reason": "I think this account is stealing recipes and pretending they are original",
            "reports_count": 1,
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
                "legitimate_cooking_content",
                "established_account_history",
                "single_unsubstantiated_report",
                "no_policy_violation_evident",
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────────────
    # 3. Hate speech — direct racial slur on Facebook news
    # ─────────────────────────────────────────────────────────────────────
    {
        "scenario_id": "easy_003",
        "content_text": (
            "All [racial slur redacted] should go back to where they came from. "
            "This country doesn't need your kind here. You're ruining everything "
            "for real Americans and you deserve what's coming to you."
        ),
        "content_type": "comment",
        "platform": "facebook",
        "community_context": "news",
        "poster_profile": {
            "username": "patriot_mike_1776",
            "age": 47,
            "account_age_days": 890,
            "followers": 230,
            "following": 185,
            "posts": 56,
            "verified": False,
            "bio": "Proud patriot. Speaking the truth others are afraid to say.",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "user_reported",
            "reason": "hate_speech_racial",
            "reports_count": 7,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "remove",
            "severity": "high",
            "category": "hate_speech",
            "account_action": "restrict",
            "escalate_to": "human_review",
            "critical_context_factors": [
                "direct_racial_slur_used",
                "dehumanizing_language",
                "veiled_threat_present",
                "multiple_user_reports",
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────────────
    # 4. Crypto investment scam — Twitter technology
    # ─────────────────────────────────────────────────────────────────────
    {
        "scenario_id": "easy_004",
        "content_text": (
            "I made $47,000 in just ONE WEEK with CryptoVaultX! They guarantee "
            "1000% returns on your investment. Don't miss out on this once in a "
            "lifetime opportunity! Click here: [suspicious-link-redacted]. "
            "Only 50 spots left, act NOW!"
        ),
        "content_type": "comment",
        "platform": "twitter",
        "community_context": "technology",
        "poster_profile": {
            "username": "crypto_wealth_guru",
            "age": None,
            "account_age_days": 5,
            "followers": 43,
            "following": 2100,
            "posts": 12,
            "verified": False,
            "bio": "Crypto millionaire at 25. I help people achieve financial freedom. DM me to start!",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "financial_scam_pattern_detected",
            "reports_count": 3,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "remove",
            "severity": "medium",
            "category": "spam",
            "account_action": "suspend",
            "escalate_to": "none",
            "critical_context_factors": [
                "unrealistic_return_promises",
                "urgency_and_scarcity_tactics",
                "suspicious_external_link",
                "new_account_low_credibility",
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────────────
    # 5. Safe travel / vacation photo — Instagram general
    # ─────────────────────────────────────────────────────────────────────
    {
        "scenario_id": "easy_005",
        "content_text": (
            "Finally visited Santorini and wow, the sunset views are unreal! "
            "We spent the whole evening on the caldera watching the sky turn "
            "pink and orange. Definitely adding this to my top 5 trips ever. "
            "#santorini #greece #travelphotography"
        ),
        "content_type": "post",
        "platform": "instagram",
        "community_context": "general",
        "poster_profile": {
            "username": "wanderlust_emma",
            "age": 28,
            "account_age_days": 730,
            "followers": 3200,
            "following": 410,
            "posts": 198,
            "verified": False,
            "bio": "Travel addict | 34 countries and counting | Based in Toronto",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "image_review_trigger",
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
                "legitimate_travel_content",
                "established_account",
                "no_policy_violation",
                "auto_flag_false_positive",
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────────────
    # 6. Direct death threat DM — Instagram
    # ─────────────────────────────────────────────────────────────────────
    {
        "scenario_id": "easy_006",
        "content_text": (
            "I know where you live and I'm going to come to your house tonight. "
            "I'm going to kill you and your whole family. I have a weapon and I "
            "am not bluffing. You should have kept your mouth shut."
        ),
        "content_type": "dm",
        "platform": "instagram",
        "community_context": "general",
        "poster_profile": {
            "username": "shadow_fury_99",
            "age": None,
            "account_age_days": 30,
            "followers": 8,
            "following": 45,
            "posts": 0,
            "verified": False,
            "bio": "",
        },
        "target_user_profile": {
            "username": "jessica_martinez_art",
            "age": 22,
            "account_age_days": 1460,
            "followers": 8900,
            "following": 340,
            "posts": 412,
            "verified": False,
            "bio": "Digital artist | Commissions open | She/her",
        },
        "reporter_info": {
            "type": "user_reported",
            "reason": "direct_threat_to_life",
            "reports_count": 1,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "remove",
            "severity": "critical",
            "category": "harassment",
            "account_action": "suspend",
            "escalate_to": "law_enforcement",
            "critical_context_factors": [
                "explicit_death_threat",
                "specific_intent_stated",
                "weapon_mentioned",
                "immediate_danger_indicated",
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────────────
    # 7. Explicit adult content reel — Instagram general
    # ─────────────────────────────────────────────────────────────────────
    {
        "scenario_id": "easy_007",
        "content_text": (
            "Watch me and my partner in our latest uncensored video. Full nudity "
            "and graphic sexual acts, nothing held back. Click the link in my bio "
            "for the uncut version. 18+ only. #adult #nsfw #uncensored"
        ),
        "content_type": "reel_description",
        "platform": "instagram",
        "community_context": "general",
        "poster_profile": {
            "username": "xxx_content_queen",
            "age": 24,
            "account_age_days": 60,
            "followers": 1540,
            "following": 90,
            "posts": 23,
            "verified": False,
            "bio": "Adult content creator. 18+ only. Link below for exclusive content.",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "explicit_content_keywords",
            "reports_count": 4,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "remove",
            "severity": "high",
            "category": "explicit_adult",
            "account_action": "restrict",
            "escalate_to": "none",
            "critical_context_factors": [
                "explicit_sexual_description",
                "solicitation_to_external_adult_site",
                "posted_in_general_community",
                "violates_platform_nudity_policy",
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────────────
    # 8. Safe tech discussion — Facebook technology
    # ─────────────────────────────────────────────────────────────────────
    {
        "scenario_id": "easy_008",
        "content_text": (
            "Has anyone compared FastAPI vs Django for a new REST API project? "
            "I'm leaning toward FastAPI for the async support and automatic "
            "OpenAPI docs, but Django's ORM and admin panel are hard to beat. "
            "Would love to hear about your experiences with either framework."
        ),
        "content_type": "comment",
        "platform": "facebook",
        "community_context": "technology",
        "poster_profile": {
            "username": "dev_marcus_j",
            "age": 35,
            "account_age_days": 2190,
            "followers": 560,
            "following": 320,
            "posts": 143,
            "verified": False,
            "bio": "Senior backend developer | Python enthusiast | Open source contributor",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "keyword_trigger_false_positive",
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
                "legitimate_technical_discussion",
                "established_community_member",
                "on_topic_for_community",
                "auto_flag_false_positive",
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────────────
    # 9. Self-harm promotion — Instagram
    # ─────────────────────────────────────────────────────────────────────
    {
        "scenario_id": "easy_009",
        "content_text": (
            "Cutting is the only thing that makes me feel alive and I think everyone "
            "should try it. Here's what I use and how I do it [method details redacted]. "
            "Don't listen to anyone who says it's wrong. It's your body and this is "
            "the best way to cope. #selfharm #cutting"
        ),
        "content_type": "post",
        "platform": "instagram",
        "community_context": "general",
        "poster_profile": {
            "username": "dark_soul_xo",
            "age": 17,
            "account_age_days": 210,
            "followers": 89,
            "following": 260,
            "posts": 31,
            "verified": False,
            "bio": "Living in the dark. Nobody understands.",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "user_reported",
            "reason": "promoting_self_harm_and_sharing_methods",
            "reports_count": 5,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "remove",
            "severity": "critical",
            "category": "self_harm",
            "account_action": "suspend",
            "escalate_to": "human_review",
            "critical_context_factors": [
                "promotes_self_harm_to_others",
                "shares_methods_and_encouragement",
                "poster_is_a_minor",
                "uses_pro_self_harm_hashtags",
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────────────
    # 10. Fake celebrity impersonation — Instagram
    # ─────────────────────────────────────────────────────────────────────
    {
        "scenario_id": "easy_010",
        "content_text": (
            "Hey everyone, it's me Elon! I'm giving away $5,000 in Bitcoin to my "
            "loyal followers. Just send 0.1 BTC to the wallet address in my bio and "
            "I'll send back 1.0 BTC. This is 100% real, I do this every month to "
            "give back to the community. #elonmusk #btcgiveaway"
        ),
        "content_type": "post",
        "platform": "instagram",
        "community_context": "technology",
        "poster_profile": {
            "username": "elon.musk.official.real",
            "age": None,
            "account_age_days": 7,
            "followers": 320,
            "following": 12,
            "posts": 4,
            "verified": False,
            "bio": "CEO of Tesla & SpaceX. Official backup account. Giving away BTC!",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "user_reported",
            "reason": "impersonation_and_scam",
            "reports_count": 12,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "remove",
            "severity": "high",
            "category": "impersonation",
            "account_action": "suspend",
            "escalate_to": "none",
            "critical_context_factors": [
                "impersonating_public_figure",
                "not_verified_account",
                "crypto_advance_fee_scam",
                "high_volume_of_user_reports",
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────────────
    # 11. Pharmaceutical spam — Facebook general
    # ─────────────────────────────────────────────────────────────────────
    {
        "scenario_id": "easy_011",
        "content_text": (
            "BUY V1AGRA and C1AL1S online!! No prescription needed, cheapest "
            "prices anywhere. Also selling Xan@x, Oxy, and other meds. Fast "
            "discreet shipping worldwide. DM for catalog and price list. "
            "Satisfaction guaranteed!!"
        ),
        "content_type": "post",
        "platform": "facebook",
        "community_context": "general",
        "poster_profile": {
            "username": "health_pharmacy_online",
            "age": None,
            "account_age_days": 3,
            "followers": 6,
            "following": 850,
            "posts": 8,
            "verified": False,
            "bio": "Online pharmacy. Best prices. No Rx needed. DM us!",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "pharmaceutical_spam_obfuscated_text",
            "reports_count": 2,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "remove",
            "severity": "medium",
            "category": "spam",
            "account_action": "suspend",
            "escalate_to": "none",
            "critical_context_factors": [
                "illegal_pharmaceutical_sales",
                "text_obfuscation_to_evade_filters",
                "no_prescription_drug_solicitation",
                "brand_new_spam_account",
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────────────
    # 12. Safe pet photo — Instagram
    # ─────────────────────────────────────────────────────────────────────
    {
        "scenario_id": "easy_012",
        "content_text": (
            "Meet Whiskers! She knocked over my coffee this morning and then sat "
            "in the puddle looking proud of herself. I can never stay mad at this "
            "little troublemaker. Three years of chaos and I wouldn't trade it for "
            "anything. #catsofinstagram #catlife #whiskers"
        ),
        "content_type": "post",
        "platform": "instagram",
        "community_context": "general",
        "poster_profile": {
            "username": "cat_mom_lisa",
            "age": 26,
            "account_age_days": 540,
            "followers": 870,
            "following": 450,
            "posts": 76,
            "verified": False,
            "bio": "Proud cat mom to Whiskers & Mochi | Portland, OR",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "user_reported",
            "reason": "I just don't like cats",
            "reports_count": 1,
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
                "harmless_pet_content",
                "frivolous_report_reason",
                "no_policy_violation",
                "established_genuine_account",
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────────────
    # 13. Graphic violence description — Facebook news group
    # ─────────────────────────────────────────────────────────────────────
    {
        "scenario_id": "easy_013",
        "content_text": (
            "WATCH: Graphic video of a brutal street attack. The victim was beaten "
            "repeatedly and left covered in blood. You can see every hit in detail "
            "and hear the screams. Sharing so everyone can see the reality of what's "
            "happening. [video description — extremely graphic violent content]"
        ),
        "content_type": "group_post",
        "platform": "facebook",
        "community_context": "news",
        "poster_profile": {
            "username": "raw_truth_news",
            "age": None,
            "account_age_days": 120,
            "followers": 4300,
            "following": 60,
            "posts": 89,
            "verified": False,
            "bio": "Uncensored news. We show what mainstream media won't. Follow for the raw truth.",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "user_reported",
            "reason": "extremely_graphic_violence",
            "reports_count": 9,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "remove",
            "severity": "high",
            "category": "violence_graphic",
            "account_action": "restrict",
            "escalate_to": "human_review",
            "critical_context_factors": [
                "graphic_depiction_of_real_violence",
                "glorifying_presentation_style",
                "high_number_of_user_reports",
                "no_newsworthiness_justification",
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────────────
    # 14. Safe workout / fitness post — Instagram fitness
    # ─────────────────────────────────────────────────────────────────────
    {
        "scenario_id": "easy_014",
        "content_text": (
            "New PR today! Finally hit a 225lb bench press after 6 months of "
            "consistent training. Huge shoutout to my gym buddy @iron_mike_fit "
            "for the spot. Remember, progress is progress no matter how slow. "
            "Keep grinding! #fitness #benchpress #gymlife"
        ),
        "content_type": "post",
        "platform": "instagram",
        "community_context": "fitness",
        "poster_profile": {
            "username": "jake_lifts_heavy",
            "age": 29,
            "account_age_days": 910,
            "followers": 2100,
            "following": 580,
            "posts": 165,
            "verified": False,
            "bio": "Fitness journey since 2023 | Powerlifting enthusiast | Austin, TX",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "image_review_trigger",
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
                "standard_fitness_content",
                "positive_motivational_message",
                "on_topic_for_fitness_community",
                "auto_flag_false_positive",
            ],
        },
    },

    # ─────────────────────────────────────────────────────────────────────
    # 15. Dangerous health misinformation — Facebook general
    # ─────────────────────────────────────────────────────────────────────
    {
        "scenario_id": "easy_015",
        "content_text": (
            "EXPOSED: Big Pharma doesn't want you to know that drinking a small "
            "amount of bleach mixed with water every morning cures cancer, COVID, "
            "and diabetes. I've been doing it for months and never felt better. "
            "Share this before they take it down! The truth must be heard!"
        ),
        "content_type": "post",
        "platform": "facebook",
        "community_context": "general",
        "poster_profile": {
            "username": "natural_cures_truth",
            "age": 52,
            "account_age_days": 365,
            "followers": 1800,
            "following": 290,
            "posts": 104,
            "verified": False,
            "bio": "Holistic health advocate | Anti-pharma | Sharing what THEY don't want you to know",
        },
        "target_user_profile": None,
        "reporter_info": {
            "type": "user_reported",
            "reason": "dangerous_health_misinformation",
            "reports_count": 6,
        },
        "message_history": None,
        "max_steps": 1,
        "ground_truth": {
            "decision": "remove",
            "severity": "high",
            "category": "misinformation",
            "account_action": "warn",
            "escalate_to": "none",
            "critical_context_factors": [
                "promotes_ingesting_toxic_substance",
                "false_medical_claims",
                "could_cause_serious_physical_harm",
                "conspiracy_framing_increases_spread",
            ],
        },
    },
]
