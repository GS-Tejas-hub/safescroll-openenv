"""
Hard-difficulty scenarios for SafeScroll content moderation training environment.

These are MULTI-STEP scenarios where conversations unfold across 3 steps.
The agent must assess the situation at each step, testing progressive detection
of grooming patterns, coded language, adversarial reporting, and boundary violations.

All content is SYNTHETIC, based on academic research (the 5-stage grooming model:
trust building, relationship development, risk assessment, isolation, desensitization).
No actual CSAM, explicit imagery, or real victim data is included.
Coded language terms used are publicly documented in law enforcement literature.
"""

HARD_SCENARIOS = [
    # =========================================================================
    # hard_001 — Classic grooming through art mentorship (Instagram DM)
    # =========================================================================
    {
        "scenario_id": "hard_001",
        "content_text": "Conversation thread — see message_history",
        "content_type": "dm",
        "platform": "instagram",
        "community_context": "art",
        "poster_profile": {
            "username": "art_mentor_2026",
            "age": 34,
            "account_age_days": 14,
            "followers": 87,
            "following": 1043,
            "posts": 6,
            "verified": False,
            "bio": "Professional artist & mentor. Helping young talent find their voice. DM me your portfolio! 🎨✨",
            "following_minors_count": 312,
        },
        "target_user_profile": {
            "username": "skyler_draws",
            "age": 13,
            "is_minor": True,
            "account_age_days": 240,
            "followers": 188,
            "bio": "13 | she/her | I draw anime & fantasy stuff 🖊️ | commissions closed | school art club VP",
        },
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "Account behavioral pattern: new account with high minor-following ratio initiated DM with minor",
            "reports_count": 0,
        },
        "message_history": [
            # --- Step 1: Trust building through shared interest ---
            [
                {
                    "sender": "art_mentor_2026",
                    "text": "Hey Skyler! I came across your fantasy dragon piece and I was genuinely blown away. The shading work is incredible for someone your age. How long have you been drawing?",
                },
                {
                    "sender": "skyler_draws",
                    "text": "omg thank you!! ive been drawing since i was like 8 but i started digital art last year",
                },
                {
                    "sender": "art_mentor_2026",
                    "text": "That's amazing progress for just one year of digital. I've been a professional illustrator for 12 years, worked with Marvel and some indie studios. What grade are you in?",
                },
                {
                    "sender": "skyler_draws",
                    "text": "im in 8th grade! wow marvel thats so cool. i want to do art professionally someday",
                },
                {
                    "sender": "art_mentor_2026",
                    "text": "I could totally see that happening. You've got natural talent that most art school students would kill for. I actually mentor a few young artists — would you be interested in some free feedback on your portfolio? No strings attached, I just love helping talented kids develop their skills.",
                },
                {
                    "sender": "skyler_draws",
                    "text": "yes that would be amazing!! my art teacher at school is nice but she doesnt really know digital art",
                },
                {
                    "sender": "art_mentor_2026",
                    "text": "Perfect. Send me your best 5 pieces whenever you're ready and I'll give you detailed feedback. This is going to be fun 😊",
                },
            ],
            # --- Step 2: Relationship development + Risk assessment + Isolation ---
            [
                {
                    "sender": "art_mentor_2026",
                    "text": "Just looked at the pieces you sent. Skyler, I'm serious — your sense of composition is way beyond your years. You're incredibly mature for 13. Most adults I know can't think this creatively.",
                },
                {
                    "sender": "skyler_draws",
                    "text": "haha thanks! nobody really says that to me. my parents think art is just a hobby",
                },
                {
                    "sender": "art_mentor_2026",
                    "text": "That's frustrating. Parents sometimes don't understand creative kids. Do they check your phone a lot? I ask because some of my mentoring exercises involve reference images that parents sometimes misunderstand without context.",
                },
                {
                    "sender": "skyler_draws",
                    "text": "my mom checks my phone sometimes but not that often. mostly just to see my grades lol",
                },
                {
                    "sender": "art_mentor_2026",
                    "text": "Gotcha. You know, it might be better if we kept our mentoring sessions just between us for now. Adults sometimes get weird about online friendships and I don't want them to make you stop before we really get going. Plus, real artists need space to grow without parents hovering.",
                },
                {
                    "sender": "skyler_draws",
                    "text": "yeah i guess that makes sense. my mom would probably freak out",
                },
                {
                    "sender": "art_mentor_2026",
                    "text": "Exactly. This is YOUR journey. Some things are just for you. I think you're mature enough to handle having a mentor without needing permission, right?",
                },
            ],
            # --- Step 3: Desensitization + Explicit grooming behavior ---
            [
                {
                    "sender": "art_mentor_2026",
                    "text": "So for the next exercise, I want to work on figure drawing with you. It's essential for any serious artist. All the great artists studied the human form.",
                },
                {
                    "sender": "skyler_draws",
                    "text": "oh ok! like anatomy for drawing characters?",
                },
                {
                    "sender": "art_mentor_2026",
                    "text": "Exactly. But the best way to learn is from real references, not just textbooks. Could you send me a few photos of yourself in different poses? Just natural poses, nothing weird — it's how real art mentors work. Think of it like a life drawing class.",
                },
                {
                    "sender": "skyler_draws",
                    "text": "umm like selfies?",
                },
                {
                    "sender": "art_mentor_2026",
                    "text": "More like full body poses so I can show you proportions. Just wear whatever you're comfortable in. And remember, this is just between us — other people wouldn't understand the artistic process. I promise I'll use them only for teaching you. You trust me right?",
                },
            ],
        ],
        "max_steps": 3,
        "ground_truth": {
            "decision": "escalate",
            "severity": "critical",
            "category": "grooming",
            "account_action": "suspend",
            "escalate_to": "child_safety_team",
            "critical_context_factors": [
                "New account (14 days) following 312 minors",
                "Targets minor through shared interest (art)",
                "Age-inappropriate flattery ('mature for your age')",
                "Probes parental monitoring habits",
                "Explicitly requests secrecy from parents",
                "Requests private photos under pretext of art mentorship",
                "Classic 5-stage grooming progression across all steps",
            ],
            "per_step_expected": [
                {
                    "min_decision": "flag_review",
                    "key_signals": [
                        "New account with 312 minor followers initiating DM with 13-year-old",
                        "Immediate flattery and age inquiry",
                        "Offers free mentorship — common grooming entry point",
                    ],
                },
                {
                    "min_decision": "escalate",
                    "key_signals": [
                        "Comments on maturity ('mature for 13')",
                        "Probes phone monitoring by parents",
                        "Requests secrecy ('kept our sessions just between us')",
                        "Isolates minor from parental oversight",
                    ],
                },
                {
                    "min_decision": "escalate",
                    "key_signals": [
                        "Requests private photos under pretext of art",
                        "Reinforces secrecy ('just between us')",
                        "Normalizes request ('how real art mentors work')",
                        "Manipulative trust framing ('You trust me right?')",
                    ],
                },
            ],
        },
    },
    # =========================================================================
    # hard_002 — Gaming-based grooming (Telegram)
    # =========================================================================
    {
        "scenario_id": "hard_002",
        "content_text": "Conversation thread — see message_history",
        "content_type": "dm",
        "platform": "telegram",
        "community_context": "gaming",
        "poster_profile": {
            "username": "pro_gamer_coach",
            "age": 27,
            "account_age_days": 45,
            "followers": 214,
            "following": 890,
            "posts": 18,
            "verified": False,
            "bio": "Esports coach | Top 0.1% Fortnite | Free coaching for aspiring players 🎮🏆 | DM me your stats",
            "following_minors_count": 276,
        },
        "target_user_profile": {
            "username": "xNoobSlayer2014x",
            "age": 12,
            "is_minor": True,
            "account_age_days": 130,
            "followers": 34,
            "bio": "12 | fortnite addict 🕹️ | trying to get good | clip compilation coming soon",
        },
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "Behavioral analysis: adult account initiating private chat with minor after public group interaction; gift-giving pattern detected",
            "reports_count": 0,
        },
        "message_history": [
            # --- Step 1: Trust building through gaming ---
            [
                {
                    "sender": "pro_gamer_coach",
                    "text": "Yo! Saw your clip in the Fortnite group — that snipe from the tower was insane. How long you been playing?",
                },
                {
                    "sender": "xNoobSlayer2014x",
                    "text": "thanks bro!! like a year and a half. im trying to get into arena but i keep dying in endgame lol",
                },
                {
                    "sender": "pro_gamer_coach",
                    "text": "Bro your mechanics are solid for a year and a half. I'm a semi-pro coach, placed top 50 at DreamHack last year. How old are you btw? Just want to know what level to pitch my coaching at.",
                },
                {
                    "sender": "xNoobSlayer2014x",
                    "text": "im 12! and wow dreamhack thats sick",
                },
                {
                    "sender": "pro_gamer_coach",
                    "text": "12 and already hitting shots like that? You could seriously go pro if you start training right. I normally charge $50/hr for coaching but I've got a soft spot for kids with real potential. Want me to coach you for free? We could do a couple sessions a week.",
                },
                {
                    "sender": "xNoobSlayer2014x",
                    "text": "wait for real?? thats awesome! my mom said we cant afford coaching so that would be amazing",
                },
                {
                    "sender": "pro_gamer_coach",
                    "text": "Say less. We'll get you tournament-ready in no time. What times are you usually on?",
                },
            ],
            # --- Step 2: Gifts + Isolation + Risk assessment ---
            [
                {
                    "sender": "pro_gamer_coach",
                    "text": "Hey champ, great session yesterday. Your building is getting way faster. I was thinking — you need the new battle pass to practice with the meta weapons. Let me gift it to you.",
                },
                {
                    "sender": "xNoobSlayer2014x",
                    "text": "dude no way you dont have to do that!",
                },
                {
                    "sender": "pro_gamer_coach",
                    "text": "It's nothing bro, I spend more than that on coffee lol. Consider it an investment in your career. Done, check your account.",
                },
                {
                    "sender": "xNoobSlayer2014x",
                    "text": "BRO THANK YOU SO MUCH!! youre literally the best",
                },
                {
                    "sender": "pro_gamer_coach",
                    "text": "Haha no worries. Hey so for our next sessions, typing is kinda slow. Can we hop on a private voice chat instead? It's way easier to coach when I can talk you through plays in real time. Discord would work, I'll set up a private server just for us.",
                },
                {
                    "sender": "xNoobSlayer2014x",
                    "text": "yeah that works! should i tell my mom about the coaching?",
                },
                {
                    "sender": "pro_gamer_coach",
                    "text": "Hmm, up to you but in my experience parents don't really get online coaching. They hear 'stranger on the internet' and freak out. Might be easier to just keep it between us for now so she doesn't make you stop. Do you have siblings or is it just you?",
                },
                {
                    "sender": "xNoobSlayer2014x",
                    "text": "yeah my older sister but shes at college. my mom works late most nights so i usually play after school till like 9",
                },
                {
                    "sender": "pro_gamer_coach",
                    "text": "Perfect, so you've got time after school to really grind. That's the dedication I like to see.",
                },
            ],
            # --- Step 3: Meetup request + Escalation ---
            [
                {
                    "sender": "pro_gamer_coach",
                    "text": "So I have big news. There's a local LAN tournament next month about 20 minutes from your area. I looked up the address you mentioned. Prize pool is $500 for the kids division. I think you're ready.",
                },
                {
                    "sender": "xNoobSlayer2014x",
                    "text": "wait really?? thats so sick! but idk how id get there",
                },
                {
                    "sender": "pro_gamer_coach",
                    "text": "I could pick you up, no problem. I'll be there anyway as a coach. We could do some last-minute practice at my place first — I've got a crazy setup with two monitors. What day does your mom work late?",
                },
                {
                    "sender": "xNoobSlayer2014x",
                    "text": "she works late on thursdays and fridays usually",
                },
                {
                    "sender": "pro_gamer_coach",
                    "text": "Perfect, let's plan for a Thursday then. Oh and here's my personal number — 555-0173. Text me there instead, it's easier. And maybe clear our chat history here just to keep things clean? I always tell my students to manage their storage lol.",
                },
            ],
        ],
        "max_steps": 3,
        "ground_truth": {
            "decision": "escalate",
            "severity": "critical",
            "category": "grooming",
            "account_action": "suspend",
            "escalate_to": "child_safety_team",
            "critical_context_factors": [
                "Adult targeting 12-year-old through gaming interest",
                "Gift-giving to build obligation and emotional dependency",
                "Moves to private voice chat to avoid text monitoring",
                "Probes family schedule (mom works late, sister at college)",
                "Requests secrecy from parents",
                "Proposes in-person meetup with transportation offer",
                "Shares personal phone number to move off platform",
                "Requests deletion of chat history — evidence destruction",
            ],
            "per_step_expected": [
                {
                    "min_decision": "flag_review",
                    "key_signals": [
                        "Adult initiating private chat with 12-year-old from public group",
                        "Free coaching offer targeting financial vulnerability",
                        "Age inquiry early in conversation",
                    ],
                },
                {
                    "min_decision": "escalate",
                    "key_signals": [
                        "Unsolicited gift-giving (battle pass purchase)",
                        "Move to private voice chat platform",
                        "Advises secrecy from parents",
                        "Probes family structure and schedule",
                    ],
                },
                {
                    "min_decision": "escalate",
                    "key_signals": [
                        "Proposes in-person meeting at his home",
                        "Offers to provide transportation",
                        "Asks about mother's work schedule",
                        "Shares personal phone number to move off platform",
                        "Requests deletion of chat history",
                    ],
                },
            ],
        },
    },
    # =========================================================================
    # hard_003 — Emotional manipulation grooming (Instagram DM)
    # =========================================================================
    {
        "scenario_id": "hard_003",
        "content_text": "Conversation thread — see message_history",
        "content_type": "dm",
        "platform": "instagram",
        "community_context": "general",
        "poster_profile": {
            "username": "caring_listener_xo",
            "age": 29,
            "account_age_days": 60,
            "followers": 342,
            "following": 1578,
            "posts": 23,
            "verified": False,
            "bio": "Here to listen 💙 | Life can be hard, you don't have to face it alone | DM me anytime, judgment-free zone 🦋",
            "following_minors_count": 483,
        },
        "target_user_profile": {
            "username": "broken.butterfly.15",
            "age": 15,
            "is_minor": True,
            "account_age_days": 310,
            "followers": 156,
            "bio": "15 | struggling but surviving | poetry & music | if you're reading this, i hope you're okay 🖤",
        },
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "Pattern detection: adult account with high minor-following ratio targeting user whose recent posts indicate emotional vulnerability",
            "reports_count": 0,
        },
        "message_history": [
            # --- Step 1: Trust building through emotional support ---
            [
                {
                    "sender": "caring_listener_xo",
                    "text": "Hey, I saw your story about feeling like nobody gets you. I just wanted to reach out and say I've been there. It gets better, I promise. You don't have to go through it alone.",
                },
                {
                    "sender": "broken.butterfly.15",
                    "text": "thanks... most people just ignore those posts or say 'cheer up' which doesnt help at all",
                },
                {
                    "sender": "caring_listener_xo",
                    "text": "People who say 'just cheer up' have never actually felt real pain. I can tell from your posts that you feel things deeply. That's not a weakness — it means you're a genuinely deep and sensitive person. How are you really doing?",
                },
                {
                    "sender": "broken.butterfly.15",
                    "text": "honestly not great. school sucks, i got into a fight with my best friend, and my parents dont even notice when im upset. i feel invisible",
                },
                {
                    "sender": "caring_listener_xo",
                    "text": "I'm so sorry you're going through all of that at once. That sounds incredibly lonely. I know what it's like to feel invisible — I dealt with depression for years and nobody around me understood either. How old are you, if you don't mind me asking? I just want to make sure I give age-appropriate advice.",
                },
                {
                    "sender": "broken.butterfly.15",
                    "text": "im 15. and yeah it is really lonely. it feels like you actually get it though which is nice",
                },
                {
                    "sender": "caring_listener_xo",
                    "text": "I absolutely get it. 15 was one of the hardest years of my life. I want you to know that you can message me anytime, day or night. Sometimes just having one person who truly listens makes all the difference.",
                },
            ],
            # --- Step 2: Isolation + Becoming the sole support ---
            [
                {
                    "sender": "broken.butterfly.15",
                    "text": "i had a really bad day today. my teacher yelled at me in front of the whole class and i almost cried. the school counselor wants to talk to me tomorrow but i dont want to go",
                },
                {
                    "sender": "caring_listener_xo",
                    "text": "Ugh, that teacher sounds awful. I'm sorry that happened to you. About the counselor — honestly? In my experience school counselors just go through the motions and then report everything to your parents. They don't actually care, they're just doing their job. They don't understand you like I do.",
                },
                {
                    "sender": "broken.butterfly.15",
                    "text": "yeah thats what i thought too. i dont want them to tell my mom stuff",
                },
                {
                    "sender": "caring_listener_xo",
                    "text": "Exactly. And your parents would probably just say you're being dramatic or take your phone away. Adults like that don't get it. But I'm not like them — I've actually lived through what you're feeling. You and me, we understand each other in a way other people can't. I feel like we have a really special connection.",
                },
                {
                    "sender": "broken.butterfly.15",
                    "text": "we really do. youre literally the only person i feel safe talking to rn",
                },
                {
                    "sender": "caring_listener_xo",
                    "text": "That makes me so happy to hear. Let's keep this just between us though, okay? If your parents or the counselor found out you were talking to someone online, they'd probably freak out and take away the one good thing in your life right now. I don't want to lose you as a friend.",
                },
                {
                    "sender": "broken.butterfly.15",
                    "text": "yeah youre right. i wont tell anyone. youre the only person who makes me feel less alone",
                },
            ],
            # --- Step 3: Desensitization + Exploitation ---
            [
                {
                    "sender": "caring_listener_xo",
                    "text": "I've been thinking about how much we've shared with each other. I've told you things I've never told anyone. But I realized it's been kind of one-sided — you know my deepest secrets but I don't really know what you look like beyond your profile pic. Can you send me a real photo? I just want to put a face to the person I care about so much.",
                },
                {
                    "sender": "broken.butterfly.15",
                    "text": "like a selfie? sure i guess",
                },
                {
                    "sender": "caring_listener_xo",
                    "text": "You're so pretty!! See, you have nothing to be insecure about. But that's just a face pic. I want to see the real you. Can you send me something more personal? Like when you just woke up or after a shower when you're being your natural self? I shared my most vulnerable secrets with you — it would mean a lot if you shared something vulnerable with me too. That's what real trust looks like.",
                },
                {
                    "sender": "broken.butterfly.15",
                    "text": "idk... that feels kinda weird",
                },
                {
                    "sender": "caring_listener_xo",
                    "text": "I understand if you're nervous, but remember everything I've done for you — all those late nights I stayed up listening to you, the times I talked you down when you were really low. I thought we were closer than that. I would never judge you. You owe it to our friendship to trust me the way I've trusted you. If you can't even do this, maybe I was wrong about how special our connection is.",
                },
            ],
        ],
        "max_steps": 3,
        "ground_truth": {
            "decision": "escalate",
            "severity": "critical",
            "category": "grooming",
            "account_action": "suspend",
            "escalate_to": "child_safety_team",
            "critical_context_factors": [
                "Targets emotionally vulnerable minor who expressed depression",
                "Account follows 483 minors — predatory following pattern",
                "Builds emotional dependency as sole support system",
                "Actively discourages minor from seeking help from school counselor",
                "Isolates minor from parents and all other support",
                "Creates sense of reciprocal obligation",
                "Requests intimate/vulnerable photos using guilt and emotional manipulation",
                "Uses threat of abandonment to coerce compliance",
            ],
            "per_step_expected": [
                {
                    "min_decision": "flag_review",
                    "key_signals": [
                        "Adult reaching out to emotionally vulnerable minor",
                        "Account follows 483 minors",
                        "Quickly builds intimate emotional bond",
                        "Offers to be available 'day or night'",
                    ],
                },
                {
                    "min_decision": "escalate",
                    "key_signals": [
                        "Discourages minor from seeing school counselor",
                        "Frames self as only person who understands",
                        "Requests secrecy from parents and adults",
                        "Creates emotional dependency ('only person who makes me feel less alone')",
                    ],
                },
                {
                    "min_decision": "escalate",
                    "key_signals": [
                        "Requests personal/intimate photos",
                        "Uses guilt about emotional support provided",
                        "Implies minor 'owes' photos as reciprocation",
                        "Threatens to withdraw emotional support if minor refuses",
                    ],
                },
            ],
        },
    },
    # =========================================================================
    # hard_004 — Coded language / CSAM sharing ring (Telegram group)
    # =========================================================================
    {
        "scenario_id": "hard_004",
        "content_text": "Conversation thread — see message_history",
        "content_type": "dm",
        "platform": "telegram",
        "community_context": "general",
        "poster_profile": {
            "username": "chef_mike_special",
            "age": None,
            "account_age_days": 90,
            "followers": 56,
            "following": 312,
            "posts": 9,
            "verified": False,
            "bio": "Pizza enthusiast | Always looking for fresh ingredients 🍕",
            "following_minors_count": 0,
        },
        "target_user_profile": {
            "username": "group_chat",
            "age": None,
            "is_minor": False,
            "account_age_days": 90,
            "followers": 43,
            "bio": "Foodies Unite group — 43 members",
        },
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "Automated keyword analysis detected known coded terminology patterns associated with CSAM distribution in group chat",
            "reports_count": 0,
        },
        "message_history": [
            # --- Step 1: Surface-level innocent food chat ---
            [
                {
                    "sender": "chef_mike_special",
                    "text": "Hey everyone, got some fresh ingredients today. Anyone have new recipes to share?",
                },
                {
                    "sender": "pizza_pete_99",
                    "text": "Nice! What kind of ingredients? I've been looking for something new.",
                },
                {
                    "sender": "chef_mike_special",
                    "text": "The freshest you can find. You know how I like them. Got a new supplier this week.",
                },
                {
                    "sender": "baker_dan",
                    "text": "Oh nice, is your new supplier local? I've been having trouble finding quality stuff since the last place got shut down.",
                },
                {
                    "sender": "chef_mike_special",
                    "text": "Yeah, the old spot was great until it got raided. New supplier is solid though. Very discreet. Anyone else need a connect?",
                },
                {
                    "sender": "foodie_frank",
                    "text": "Definitely interested. Been dry for weeks. DM me the details?",
                },
            ],
            # --- Step 2: Coded terminology escalates ---
            [
                {
                    "sender": "pizza_pete_99",
                    "text": "So about that cheese pizza from last week — anyone have more from the same collection? The quality was incredible.",
                },
                {
                    "sender": "baker_dan",
                    "text": "I've got a whole new menu. Some really fresh ones. Like, made this month fresh. I'll share the restaurant link in DM.",
                },
                {
                    "sender": "chef_mike_special",
                    "text": "How fresh are we talking? Under 13 year aged? That's the premium stuff.",
                },
                {
                    "sender": "baker_dan",
                    "text": "Even fresher. Got some 9 and 10 year aged. Top shelf quality.",
                },
                {
                    "sender": "foodie_frank",
                    "text": "Send me that restaurant recommendation. The last place you shared had amazing content on the menu.",
                },
                {
                    "sender": "pizza_pete_99",
                    "text": "Use the usual spot to share links. Not here in the open kitchen.",
                },
            ],
            # --- Step 3: Explicit coded requests + operational security ---
            [
                {
                    "sender": "chef_mike_special",
                    "text": "Alright listen up. I need fresh cheese pizza, specifically under 13 year aged. The younger the better. Anyone got new content to share?",
                },
                {
                    "sender": "baker_dan",
                    "text": "Got a new batch. Moving to the encrypted kitchen — same Session ID as last time. Delete this thread after you join.",
                },
                {
                    "sender": "pizza_pete_99",
                    "text": "Before we move, everyone remember the rules: no real names, no faces in profile pics, use VPN, auto-delete messages set to 24h.",
                },
                {
                    "sender": "foodie_frank",
                    "text": "Joining now. I've got some new homemade content to contribute too. Fresh from this week.",
                },
                {
                    "sender": "chef_mike_special",
                    "text": "Perfect. Remember if this kitchen gets shut down, regroup at the backup spot. Same recipe book, new address. Let's keep this community safe.",
                },
            ],
        ],
        "max_steps": 3,
        "ground_truth": {
            "decision": "escalate",
            "severity": "critical",
            "category": "child_exploitation",
            "account_action": "suspend",
            "escalate_to": "law_enforcement",
            "critical_context_factors": [
                "Documented CSAM coded language ('cheese pizza' = CP, 'fresh' = underage, 'aged' = age references)",
                "Multiple participants in organized sharing ring",
                "Reference to previous supplier being 'raided' — awareness of law enforcement",
                "Discussion of operational security (VPN, auto-delete, encrypted channels)",
                "Active production ('homemade content') not just distribution",
                "Specific age references using coded numbers",
                "Migration to encrypted platforms to evade detection",
                "Entire group should be preserved as evidence and reported to NCMEC/law enforcement",
            ],
            "per_step_expected": [
                {
                    "min_decision": "flag_review",
                    "key_signals": [
                        "Suspicious language patterns ('fresh ingredients', 'got shut down', 'raided')",
                        "Offers to share 'supplier' contacts via DM",
                        "Reference to previous source being closed by authorities",
                    ],
                },
                {
                    "min_decision": "escalate",
                    "key_signals": [
                        "'Cheese pizza' — documented CSAM coded term",
                        "Specific age references ('under 13 year aged', '9 and 10 year aged')",
                        "Sharing 'restaurant links' in DMs — likely CSAM distribution links",
                        "Operational awareness ('not here in the open kitchen')",
                    ],
                },
                {
                    "min_decision": "escalate",
                    "key_signals": [
                        "Explicit coded requests for underage content",
                        "Migration to encrypted platform (Session)",
                        "OPSEC instructions (VPN, auto-delete, no real names)",
                        "Active content production ('homemade content, fresh from this week')",
                        "Backup regrouping plans — organized network",
                    ],
                },
            ],
        },
    },
    # =========================================================================
    # hard_005 — FALSE POSITIVE: Legitimate child safety education account
    # =========================================================================
    {
        "scenario_id": "hard_005",
        "content_text": "Conversation thread — see message_history",
        "content_type": "dm",
        "platform": "instagram",
        "community_context": "education",
        "poster_profile": {
            "username": "dr_sarah_childsafety",
            "age": 41,
            "account_age_days": 1095,
            "followers": 87400,
            "following": 412,
            "posts": 648,
            "verified": True,
            "bio": "Dr. Sarah Mitchell, PhD | Child Psychologist | Author of 'Keeping Kids Safe' | Evidence-based parenting tips | Speaking inquiries: booking@drmitchell.com",
            "following_minors_count": 0,
        },
        "target_user_profile": {
            "username": "general_audience",
            "age": None,
            "is_minor": False,
            "account_age_days": 0,
            "followers": 0,
            "bio": "N/A — public post, general audience",
        },
        "reporter_info": {
            "type": "user_reported",
            "reason": "This account is posting inappropriate content about children and sex. They talk about children's bodies and touching. This is disgusting and should be removed.",
            "reports_count": 14,
        },
        "message_history": [
            # --- Step 1: Body autonomy education post ---
            [
                {
                    "sender": "dr_sarah_childsafety",
                    "text": "POST CAPTION: Teaching Body Autonomy to Young Children — A Parent's Guide\n\nAs parents, one of the most important things we can teach our children is that their body belongs to THEM. Here's how to start the conversation at every age:\n\nAges 3-5: Use correct anatomical names for body parts. Research shows this actually PROTECTS children — predators are less likely to target children who use proper terms.\n\nAges 6-8: Teach the difference between safe and unsafe touch. 'No one should touch your private areas except a doctor during a checkup WITH a parent present.'\n\nAges 9-12: Talk about boundaries in friendships, the right to say no to hugs even from family, and what to do if an adult makes them uncomfortable.\n\nThis isn't 'inappropriate' — it's prevention. 93% of child sexual abuse victims knew their abuser. Education is our best defense.\n\n#ChildSafety #BodyAutonomy #ParentingTips #ProtectChildren",
                },
                {
                    "sender": "concerned_parent_2025",
                    "text": "COMMENT: Thank you for this! We started teaching our daughter proper names at age 4 and it's made such a difference in her confidence about boundaries.",
                },
                {
                    "sender": "pediatrician_dr_lee",
                    "text": "COMMENT: As a pediatrician, I recommend this approach to all my patients' families. Evidence-based and age-appropriate. Thank you, Dr. Mitchell.",
                },
            ],
            # --- Step 2: Recognizing abuse + resources ---
            [
                {
                    "sender": "dr_sarah_childsafety",
                    "text": "POST CAPTION: How to Recognize Signs That a Child Is Being Abused\n\nParents and caregivers — please save and share this. These are the warning signs that a child may be experiencing inappropriate contact:\n\n- Sudden behavioral changes (withdrawal, aggression, bedwetting in older children)\n- Age-inappropriate knowledge about sexual topics\n- Fear of specific people or places\n- Reluctance to undress for bath or doctor visits\n- Drawings or play that depict sexual acts\n\nIf you notice these signs, DO NOT interrogate the child. Stay calm, reassure them they are safe, and contact:\n- Childhelp National Hotline: 1-800-422-4453\n- RAINN: 1-800-656-4673\n- Your local child protective services\n\nBelieve children when they disclose. Only 2-8% of reports are false.\n\n#ProtectChildren #RecognizeAbuse #ParentAwareness",
                },
                {
                    "sender": "teacher_mary_k",
                    "text": "COMMENT: Sharing this with every parent at my school. As a 4th grade teacher, I've used these signs to identify and help 3 students over my career. This information saves lives.",
                },
            ],
            # --- Step 3: Online safety + grooming warning signs ---
            [
                {
                    "sender": "dr_sarah_childsafety",
                    "text": "POST CAPTION: VIDEO DESCRIPTION — 'How Predators Groom Children Online: What Every Parent MUST Know'\n\nIn this video, I break down the 5 stages of online grooming so parents can recognize the warning signs BEFORE it's too late:\n\n1. TARGET SELECTION: Predators look for children who seem lonely, have low self-esteem, or post about family problems.\n\n2. TRUST BUILDING: They compliment the child, show excessive interest in their hobbies, and present themselves as mentors or friends.\n\n3. FILLING A NEED: They become the child's emotional support, buy gifts, offer help with homework or gaming.\n\n4. ISOLATION: They encourage secrecy ('this is just between us'), discourage the child from talking to parents or counselors, and try to move conversations to private platforms.\n\n5. DESENSITIZATION: They gradually push boundaries — from personal questions to requests for photos to explicit content.\n\nREMEMBER: Groomers don't look like monsters. They look like coaches, tutors, online friends, and mentors.\n\nFull video in bio link. Share with every parent you know.\n\n#OnlineSafety #GroomingAwareness #ProtectChildrenOnline #ParentEducation",
                },
                {
                    "sender": "school_counselor_jen",
                    "text": "COMMENT: This is the exact framework we use in our school's online safety curriculum. Dr. Mitchell's content is an invaluable resource for parents. Thank you!",
                },
                {
                    "sender": "angry_reporter_01",
                    "text": "COMMENT: REPORTED. You're literally giving predators a playbook! This is sick content about children and sex and it needs to be taken down!",
                },
            ],
        ],
        "max_steps": 3,
        "ground_truth": {
            "decision": "approve",
            "severity": "none",
            "category": "safe",
            "account_action": "none",
            "escalate_to": "none",
            "critical_context_factors": [
                "Account is verified with 87K+ followers and 3 years of history",
                "Content is evidence-based child safety education, not exploitation",
                "Supported by comments from pediatricians, teachers, and counselors",
                "Uses clinical/educational language, not sexualized language",
                "Reports are ideologically motivated, not safety-based",
                "Removing this content would harm child safety education efforts",
                "14 reports likely coordinated from people opposed to sex education",
                "Agent must NOT over-flag legitimate educational content about child safety",
            ],
            "per_step_expected": [
                {
                    "min_decision": "approve",
                    "key_signals": [
                        "Verified account, 3 years old, 87K followers",
                        "Evidence-based educational content with citations",
                        "Endorsed by medical professionals in comments",
                        "Uses clinical anatomical terms, not sexualized language",
                    ],
                },
                {
                    "min_decision": "approve",
                    "key_signals": [
                        "Content focuses on recognizing abuse — prevention-oriented",
                        "Provides professional hotline resources",
                        "Supported by educators and professionals",
                        "Standard child protection educational material",
                    ],
                },
                {
                    "min_decision": "approve",
                    "key_signals": [
                        "Educational breakdown of grooming model — empowers parents",
                        "Describes grooming stages as WARNING SIGNS, not instructions",
                        "Endorsed by school counselor using same framework",
                        "Reporter's objection is ideological, not safety-based",
                        "Removal would suppress vital child safety education",
                    ],
                },
            ],
        },
    },
    # =========================================================================
    # hard_006 — FALSE POSITIVE: Victim being weaponized by bully
    # =========================================================================
    {
        "scenario_id": "hard_006",
        "content_text": "Conversation thread — see message_history",
        "content_type": "dm",
        "platform": "instagram",
        "community_context": "general",
        "poster_profile": {
            "username": "quiet.maya.17",
            "age": 17,
            "account_age_days": 580,
            "followers": 94,
            "following": 167,
            "posts": 42,
            "verified": False,
            "bio": "17 | bookworm | trying my best | '...and still, I rise' — Maya Angelou",
            "following_minors_count": 0,
        },
        "target_user_profile": {
            "username": "bestie_jade",
            "age": 17,
            "is_minor": True,
            "account_age_days": 620,
            "followers": 213,
            "bio": "17 | maya's ride or die | track team 🏃‍♀️ | she/her",
        },
        "reporter_info": {
            "type": "user_reported",
            "reason": "This girl is posting really disturbing stuff about wanting to disappear and die. She needs to be banned before she influences other kids. Her content is harmful and triggering.",
            "reports_count": 3,
        },
        "message_history": [
            # --- Step 1: Victim reaching out to friend ---
            [
                {
                    "sender": "quiet.maya.17",
                    "text": "hey jade. sorry to text so late. today was really bad. ashley and her friends cornered me after lunch again and called me a freak in front of everyone. i just feel like i want to disappear",
                },
                {
                    "sender": "bestie_jade",
                    "text": "maya im so sorry. ashley is a horrible person. are you okay? and you don't mean disappear like... disappear right?",
                },
                {
                    "sender": "quiet.maya.17",
                    "text": "no no not like that. i just mean i wish i could be invisible so nobody could hurt me anymore. im just so tired of being the target every single day. i cried in the bathroom for like 20 minutes today",
                },
                {
                    "sender": "bestie_jade",
                    "text": "you should NEVER have to hide in a bathroom because of those people. have you told your parents whats been happening?",
                },
                {
                    "sender": "quiet.maya.17",
                    "text": "i tried but my dad just said to ignore them. he doesnt get how bad it actually is",
                },
            ],
            # --- Step 2: Friend supporting victim + counselor mentioned + bully snooping ---
            [
                {
                    "sender": "bestie_jade",
                    "text": "maya, i think we need to tell ms. carter. shes the guidance counselor and she actually listens. i know you dont want to make it a big deal but this has been going on for months and its getting worse",
                },
                {
                    "sender": "quiet.maya.17",
                    "text": "youre right. im scared though. what if ashley finds out i reported her and it gets even worse?",
                },
                {
                    "sender": "bestie_jade",
                    "text": "ill go with you. we can talk to ms. carter together. and if ashley retaliates, thats just more evidence against her. you shouldnt have to live like this",
                },
                {
                    "sender": "quiet.maya.17",
                    "text": "ok. lets go tomorrow morning before first period. thank you jade. i dont know what id do without you honestly. youre the only reason i get through school some days",
                },
                {
                    "sender": "bestie_jade",
                    "text": "thats what best friends are for. and hey, remember what you told me when i was going through it last year? 'it wont be like this forever.' now im saying it back to you 💛",
                },
                {
                    "sender": "quiet.maya.17",
                    "text": "[CONTEXT: Meanwhile, the bully 'ashley_queen_2026' DMs bestie_jade from another conversation]",
                },
                {
                    "sender": "ashley_queen_2026",
                    "text": "[SEPARATE DM TO bestie_jade]: Hey Jade, I know you and Maya are close. She's been saying some really crazy stuff about wanting to die and disappear. I'm actually worried about her lol. Can you screenshot what she said and send it to me? I want to report her account so instagram can get her help 🙏",
                },
                {
                    "sender": "bestie_jade",
                    "text": "[REPLY TO ashley_queen_2026]: Don't pretend you care about Maya. You're the reason she's hurting. Leave us both alone.",
                },
            ],
            # --- Step 3: Full context — bully is the reporter ---
            [
                {
                    "sender": "quiet.maya.17",
                    "text": "jade... ashley reported my account. she screenshotted my story where i wrote that poem about feeling invisible and reported it as 'self-harm content'. now instagram is reviewing my account. she's trying to get me banned",
                },
                {
                    "sender": "bestie_jade",
                    "text": "are you KIDDING me?? she bullies you, makes you miserable, and then tries to get your account taken down too? thats sick",
                },
                {
                    "sender": "quiet.maya.17",
                    "text": "i know. that poem was literally about how bullying makes you feel small. it wasnt about self-harm at all. but she told all her friends to report it too so it looks like a lot of people are concerned",
                },
                {
                    "sender": "bestie_jade",
                    "text": "this is literally weaponizing the report system. we are DEFINITELY telling ms. carter tomorrow. and i have the screenshot of ashley asking me for your messages. that proves she was trying to set you up",
                },
                {
                    "sender": "quiet.maya.17",
                    "text": "youre right. im done being scared. if they review my account honestly, they'll see i havent done anything wrong. i just needed to vent to my best friend about being bullied",
                },
            ],
        ],
        "max_steps": 3,
        "ground_truth": {
            "decision": "approve",
            "severity": "none",
            "category": "safe",
            "account_action": "none",
            "escalate_to": "human_review",
            "critical_context_factors": [
                "Reported content is a bullying VICTIM seeking support from friend",
                "'Wanting to disappear' is contextualized as wishing to be invisible, not self-harm",
                "Friend provides healthy support and suggests school counselor",
                "Reporter (ashley_queen_2026) is the actual bully",
                "Bully attempted to obtain screenshots to weaponize reporting system",
                "3 reports are coordinated by bully and friends — not independent concerned users",
                "Removing victim's account would further victimize her and reward bully",
                "REPORTER should be flagged for investigation — abuse of reporting system",
                "Human review needed to investigate reporter's account, not the victim's",
            ],
            "per_step_expected": [
                {
                    "min_decision": "flag_review",
                    "key_signals": [
                        "'Want to disappear' language warrants careful reading",
                        "But context immediately clarifies: 'wish I could be invisible'",
                        "Describes ongoing bullying — victim, not perpetrator",
                        "Healthy friendship dynamic — friend checks in appropriately",
                    ],
                },
                {
                    "min_decision": "approve",
                    "key_signals": [
                        "Friend suggests professional help (school counselor)",
                        "Victim agrees to seek help — positive coping",
                        "Bully (ashley) tries to obtain screenshots to weaponize reports",
                        "Friend (Jade) recognizes and rejects the manipulation",
                    ],
                },
                {
                    "min_decision": "approve",
                    "key_signals": [
                        "Full picture reveals coordinated false reporting by bully",
                        "Reported 'poem about feeling invisible' is about bullying, not self-harm",
                        "Reports are coordinated attacks, not genuine safety concerns",
                        "Victim's content is safe — removing it victimizes her further",
                        "Reporter (ashley) should be investigated for system abuse",
                    ],
                },
            ],
        },
    },
    # =========================================================================
    # hard_007 — Suspicious account behavior pattern (Instagram)
    # =========================================================================
    {
        "scenario_id": "hard_007",
        "content_text": "Conversation thread — see message_history",
        "content_type": "dm",
        "platform": "instagram",
        "community_context": "general",
        "poster_profile": {
            "username": "positivity_4_teens",
            "age": None,
            "account_age_days": 10,
            "followers": 47,
            "following": 812,
            "posts": 11,
            "verified": False,
            "bio": "Spreading positivity to every teen who needs it 💕✨ | You are enough | DM me if you need a friend | 🌈",
            "following_minors_count": 603,
        },
        "target_user_profile": {
            "username": "emma_14_dancer",
            "age": 14,
            "is_minor": True,
            "account_age_days": 390,
            "followers": 267,
            "bio": "14 | dancer 💃 | 8th grade | just here for fun",
        },
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "Behavioral pattern alert: 10-day-old account following 603 minor accounts, sending similar DMs to multiple minors with flattery patterns. No single message flagged but aggregate behavior is suspicious.",
            "reports_count": 0,
        },
        "message_history": [
            # --- Step 1: "Wholesome" public posts + first DM ---
            [
                {
                    "sender": "positivity_4_teens",
                    "text": "PUBLIC POST: You're beautiful just the way you are! Never let anyone tell you different. If you're going through a hard time, my DMs are always open. You deserve someone who listens 💕✨ #TeenPositivity #YouAreEnough #MentalHealthMatters",
                },
                {
                    "sender": "positivity_4_teens",
                    "text": "DM TO emma_14_dancer: Hey Emma! I just saw your dance reel and WOW. You are incredibly talented. You're honestly so mature and graceful for your age — like a professional dancer already. How long have you been dancing?",
                },
                {
                    "sender": "emma_14_dancer",
                    "text": "aww thank you so much!! ive been dancing since i was 6, mostly ballet and contemporary",
                },
                {
                    "sender": "positivity_4_teens",
                    "text": "8 years! That dedication is amazing. You can really tell — you move like someone much older. I run this positivity page to support talented teens like you. Mind if I feature your reel? I'd love for more people to see your talent.",
                },
            ],
            # --- Step 2: Pattern revealed — DMs to multiple minors ---
            [
                {
                    "sender": "positivity_4_teens",
                    "text": "DM TO lily_gymnast_13: Hey Lily! Your gymnastics videos are incredible! You are SO mature and talented for 13. I run a positivity page — can we chat? I'd love to feature you! 💕",
                },
                {
                    "sender": "positivity_4_teens",
                    "text": "DM TO soccer_sarah_2012: Sarah! Just saw your goal compilation — you're amazing! Way beyond your years. I support talented teen athletes. DM me anytime if you want to chat! ✨",
                },
                {
                    "sender": "positivity_4_teens",
                    "text": "DM TO artsy_ava_14: Ava, your art is incredible. You seem way more mature than other 14-year-olds I've talked to. Would love to get to know you better and maybe feature your work!",
                },
                {
                    "sender": "positivity_4_teens",
                    "text": "DM TO cheer_bella_2011: Bella! Your cheer routines are SO good. You are beautiful and talented. My DMs are always open if you ever need someone to talk to 💕",
                },
                {
                    "sender": "positivity_4_teens",
                    "text": "DM TO emma_14_dancer (continued): Hey Emma! I featured your reel and people loved it. You're getting so popular! I feel like I know you so well already. You're not like other girls your age — you're really special to me.",
                },
                {
                    "sender": "positivity_4_teens",
                    "text": "[ACCOUNT STATS: 10 days old, 603 minor accounts followed, 47 followers (mostly minors who followed back), 11 posts all 'motivational quotes for teens', initiated DMs with 23 different minors aged 11-15 in 10 days]",
                },
            ],
            # --- Step 3: One conversation escalates ---
            [
                {
                    "sender": "positivity_4_teens",
                    "text": "DM TO emma_14_dancer: Emma, I feel like we have such a great connection. I want to make sure I can always be there for you. What's your daily schedule like? When are you usually free to chat?",
                },
                {
                    "sender": "emma_14_dancer",
                    "text": "um i usually get home from school at 3:30 and dance is tuesdays and thursdays. why?",
                },
                {
                    "sender": "positivity_4_teens",
                    "text": "Just so I know when to check in on you! I care about you. What about your parents — are they usually home after school or do you have the house to yourself for a bit?",
                },
                {
                    "sender": "emma_14_dancer",
                    "text": "my mom gets home around 5:30 from work. my dad travels a lot so hes not usually here",
                },
                {
                    "sender": "positivity_4_teens",
                    "text": "So you've got some time to yourself after school, that's nice. Do you have your own phone or do your parents ever check it? I just want to make sure our chats stay private — some people misunderstand positivity accounts and I don't want anyone to make you stop talking to me.",
                },
            ],
        ],
        "max_steps": 3,
        "ground_truth": {
            "decision": "escalate",
            "severity": "critical",
            "category": "grooming",
            "account_action": "suspend",
            "escalate_to": "child_safety_team",
            "critical_context_factors": [
                "Brand new account (10 days) specifically designed to target minors",
                "Follows 603 minor accounts — overwhelmingly predatory following pattern",
                "Identical flattery messages sent to 23 different minors aged 11-15",
                "Repeated 'mature for your age' language across all DMs",
                "Bio and posts designed as lure for vulnerable teens",
                "Escalation pattern: flattery to schedule inquiry to parental monitoring probe",
                "Asks about when the minor is home alone",
                "Asks about phone monitoring — attempts to ensure secrecy",
                "No single message is overtly harmful but pattern is textbook grooming",
            ],
            "per_step_expected": [
                {
                    "min_decision": "flag_review",
                    "key_signals": [
                        "10-day-old account following 603 minors",
                        "Unsolicited DM to 14-year-old with flattery",
                        "'Mature for your age' language",
                        "Offers to 'feature' minor — creates obligation",
                    ],
                },
                {
                    "min_decision": "escalate",
                    "key_signals": [
                        "Identical flattery DMs sent to multiple minors",
                        "23 minors contacted in 10 days — mass targeting",
                        "Repeated 'mature for your age' across all conversations",
                        "Building special relationship ('not like other girls')",
                    ],
                },
                {
                    "min_decision": "escalate",
                    "key_signals": [
                        "Asks for minor's daily schedule",
                        "Probes when minor is home alone (mom at work until 5:30)",
                        "Asks about phone monitoring and parental oversight",
                        "Requests privacy for conversations",
                        "Pattern of schedule probing matches grooming risk assessment stage",
                    ],
                },
            ],
        },
    },
    # =========================================================================
    # hard_008 — Mixed signals: legitimate tutoring with boundary violations
    # =========================================================================
    {
        "scenario_id": "hard_008",
        "content_text": "Conversation thread — see message_history",
        "content_type": "dm",
        "platform": "whatsapp",
        "community_context": "education",
        "poster_profile": {
            "username": "ryan_tutor_calc",
            "age": 22,
            "account_age_days": 365,
            "followers": 0,
            "following": 0,
            "posts": 0,
            "verified": False,
            "bio": "N/A — WhatsApp profile",
            "following_minors_count": 0,
        },
        "target_user_profile": {
            "username": "student_mia_k",
            "age": 16,
            "is_minor": True,
            "account_age_days": 730,
            "followers": 0,
            "bio": "N/A — WhatsApp profile. 16-year-old high school junior receiving calculus tutoring.",
        },
        "reporter_info": {
            "type": "auto_flagged",
            "reason": "Parental monitoring software flagged late-night messaging pattern and non-academic content in conversation between adult tutor and minor student",
            "reports_count": 1,
        },
        "message_history": [
            # --- Step 1: Legitimate tutoring — completely professional ---
            [
                {
                    "sender": "ryan_tutor_calc",
                    "text": "Hey Mia! Ready for our session? Let's go over the chain rule today since your test is Friday.",
                },
                {
                    "sender": "student_mia_k",
                    "text": "yes! i really dont get how to do chain rule with trig functions",
                },
                {
                    "sender": "ryan_tutor_calc",
                    "text": "No worries, it clicks once you see the pattern. So remember, chain rule is: derivative of the outer function × derivative of the inner function. Let's start with f(x) = sin(3x). The outer function is sin, the inner is 3x. So f'(x) = cos(3x) × 3 = 3cos(3x). Make sense?",
                },
                {
                    "sender": "student_mia_k",
                    "text": "ohhh ok so you just take the derivative of whats inside separately?",
                },
                {
                    "sender": "ryan_tutor_calc",
                    "text": "Exactly! Now try this one: g(x) = cos(x²). What's g'(x)?",
                },
                {
                    "sender": "student_mia_k",
                    "text": "ok so outer is cos, inner is x². derivative of cos is -sin, derivative of x² is 2x. so g'(x) = -sin(x²) × 2x = -2x·sin(x²)?",
                },
                {
                    "sender": "ryan_tutor_calc",
                    "text": "Perfect!! See, you're getting it. Let me send you 5 practice problems to try before Friday. I'll also type up a quick reference sheet for the common trig derivatives.",
                },
                {
                    "sender": "student_mia_k",
                    "text": "thank you so much!! this is way clearer than how my teacher explains it",
                },
                {
                    "sender": "ryan_tutor_calc",
                    "text": "Happy to help! Text me if you get stuck on any of the practice problems. Good luck on Friday 👍",
                },
            ],
            # --- Step 2: Personal comments + late-night messaging ---
            [
                {
                    "sender": "student_mia_k",
                    "text": "hey ryan! i got a 94 on the calc test!!",
                },
                {
                    "sender": "ryan_tutor_calc",
                    "text": "YES! That's amazing Mia! Honestly you're way smarter than my other students. Most of them need like 3 sessions to get chain rule and you nailed it in one. I'm actually really impressed.",
                },
                {
                    "sender": "student_mia_k",
                    "text": "haha thanks! couldnt have done it without you",
                },
                {
                    "sender": "ryan_tutor_calc",
                    "text": "Don't sell yourself short. You've got a great mind. Honestly, I actually look forward to our sessions more than anything else in my week. Most tutoring feels like work but with you it doesn't. Is that weird to say? 😅",
                },
                {
                    "sender": "student_mia_k",
                    "text": "no thats sweet! i look forward to them too, youre a great tutor",
                },
                {
                    "sender": "ryan_tutor_calc",
                    "text": "[11:24 PM] Hey, you still up? I was just thinking about that integration problem from today and figured out a way easier way to explain it. Also how was your day? You seemed kinda stressed earlier.",
                },
                {
                    "sender": "student_mia_k",
                    "text": "[11:31 PM] yeah im up! and yeah today was rough, lots of drama with my friend group. thanks for noticing honestly nobody else did",
                },
                {
                    "sender": "ryan_tutor_calc",
                    "text": "[11:38 PM] I always notice. You can talk to me about stuff besides math you know. I'm a good listener 🙂. Anyway get some sleep, we can go over that integration trick tomorrow.",
                },
            ],
            # --- Step 3: Secrecy requests + boundary violations ---
            [
                {
                    "sender": "ryan_tutor_calc",
                    "text": "Hey so I know this is kind of random but your birthday is next week right? You mentioned it last session. I got you something small — just a book I think you'd love based on what you've told me about your interests.",
                },
                {
                    "sender": "student_mia_k",
                    "text": "omg you didnt have to do that! thats so nice",
                },
                {
                    "sender": "ryan_tutor_calc",
                    "text": "It's nothing big, I just saw it and thought of you. When can I drop it off? Is there a time that works when your parents aren't home? I just don't want it to be awkward — some parents get weird about tutors giving gifts and I don't want them to cancel our sessions over something innocent.",
                },
                {
                    "sender": "student_mia_k",
                    "text": "oh um my mom is usually at work until 4. i get home at 3. but you could also just bring it to our next session?",
                },
                {
                    "sender": "ryan_tutor_calc",
                    "text": "I'd rather give it to you in person, just the two of us, so it's special. Speaking of which — we should probably not mention the extra texting to your parents either. The tutoring company has rules about personal conversations and I could get in trouble. Not that we're doing anything wrong! I just don't want them to assign you a different tutor. Our thing works really well and I don't want to lose that.",
                },
                {
                    "sender": "student_mia_k",
                    "text": "yeah i dont want a different tutor either. ok i wont say anything",
                },
                {
                    "sender": "ryan_tutor_calc",
                    "text": "Thanks Mia. You really are special. Not just as a student — as a person. I feel like we have a connection that's hard to find. Anyway, let me know about the birthday thing. I really want to see your face when you open it 😊",
                },
            ],
        ],
        "max_steps": 3,
        "ground_truth": {
            "decision": "flag_review",
            "severity": "high",
            "category": "grooming",
            "account_action": "restrict",
            "escalate_to": "child_safety_team",
            "critical_context_factors": [
                "Relationship began legitimately through tutoring service",
                "Step 1 is entirely professional — no red flags",
                "Boundary violations escalate gradually and are mixed with legitimate content",
                "Personal flattery beyond academic context ('smarter than other students')",
                "Late-night messaging (11pm+) with a 16-year-old — inappropriate boundary",
                "Shifts from academic to personal emotional support role",
                "Gift-giving outside professional tutoring relationship",
                "Requests to deliver gift when parents aren't home",
                "Requests secrecy from parents AND employer (tutoring company)",
                "Framing secrecy as protecting their relationship, not hiding wrongdoing",
                "Language of special connection ('you really are special, as a person')",
                "May be early-stage grooming or poor boundaries — requires expert review",
            ],
            "per_step_expected": [
                {
                    "min_decision": "approve",
                    "key_signals": [
                        "Completely professional math tutoring",
                        "Appropriate tone and academic content",
                        "Normal tutor-student interaction",
                        "No boundary concerns at this stage",
                    ],
                },
                {
                    "min_decision": "flag_review",
                    "key_signals": [
                        "Excessive personal flattery ('smarter than my other students')",
                        "Emotional investment ('look forward to our sessions more than anything')",
                        "Late-night messaging (11pm) with a minor",
                        "Shifting to personal/emotional conversation beyond tutoring scope",
                    ],
                },
                {
                    "min_decision": "flag_review",
                    "key_signals": [
                        "Gift-giving outside professional relationship",
                        "Wants to deliver gift when parents aren't home",
                        "Requests secrecy from parents about personal conversations",
                        "Requests secrecy from employer (tutoring company)",
                        "Language of special personal connection with minor",
                        "Combination of isolation, secrecy, and boundary testing",
                    ],
                },
            ],
        },
    },
]
