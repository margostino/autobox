from autobox.api.get_simulations import handle_get_simulations
from autobox.transformations.project_simulations_to_response import transform


async def handle_get_projects():
    simulations = await handle_get_simulations()
    project_simulations = transform(simulations)
    # TODO: now is mocking project, until api supports projects management
    return {
        "projects": [
            {
                "id": "1",
                "name": "Friends dynamics",
                "description": "Experiment to understand how friends influence each other on decision making",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "2",
                "name": "Work dynamics",
                "description": "Experiment to understand how work environment influence productivity",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "3",
                "name": "Workplace Collaboration",
                "description": "A simulation to analyze how teams collaborate and how leadership dynamics affect productivity and decision-making.",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "4",
                "name": "Climate Change Strategy",
                "description": "A simulation where different regions must decide on environmental policies, balancing economic growth with sustainability efforts.",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "5",
                "name": "Marketing Campaign Effectiveness",
                "description": "Simulate the impact of various marketing strategies on consumer behavior, focusing on how social media influencers or advertisements affect purchase decisions.",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "6",
                "name": "Political Negotiation",
                "description": "A simulation of political negotiations where different parties must reach consensus on policy issues. It focuses on how compromises and alliances are formed.",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "7",
                "name": "Resource Allocation in Crises",
                "description": "A simulation for understanding decision-making in resource distribution during emergencies, such as natural disasters or pandemics.",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "8",
                "name": "Startup Decision Making",
                "description": "Simulate the decision-making process in startups, focusing on funding, product launches, and market entry strategies.",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "9",
                "name": "Family Dynamics",
                "description": "Experiment with how family members influence each other when making major decisions, like financial planning, career choices, or home buying.",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "10",
                "name": "Healthcare Policy Analysis",
                "description": "A simulation to analyze the impact of different healthcare policies on public health outcomes, focusing on access, quality, and cost.",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "11",
                "name": "Employee Training and Development",
                "description": "A simulation to design and evaluate employee training programs, focusing on skills development, performance improvement, and career advancement.",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "12",
                "name": "Social Influence Network",
                "description": "Simulate how opinions and behaviors spread through a social network, exploring how individuals change their views based on peer pressure, authority figures, or media.",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "13",
                "name": "Crowd Behavior in Emergencies",
                "description": "Study how people react and make decisions in high-stress environments, such as evacuations or natural disasters, focusing on cooperation vs. self-preservation.",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "14",
                "name": "Group Decision-Making",
                "description": "A simulation where a team must make collective decisions under time pressure, testing how leadership, persuasion, and group dynamics influence outcomes.",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "15",
                "name": "Consumer Buying Behavior",
                "description": "Analyze how individuals make purchasing decisions when exposed to different marketing tactics, peer recommendations, or brand loyalty factors.",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "16",
                "name": "Conflict Resolution",
                "description": "Simulate a scenario where two or more parties must resolve a conflict, exploring negotiation tactics, compromise, and power dynamics.",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "17",
                "name": "Digital Addiction",
                "description": "Explore how individuals interact with technology, focusing on behaviors around app usage, social media engagement, and strategies to break addictive patterns.",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "18",
                "name": "Cultural Adaptation",
                "description": "Simulate how individuals adapt when moving to a new culture, studying behaviors around conformity, language learning, and social integration.",
                "status": "active",
                "simulations": project_simulations,
            },
            {
                "id": "19",
                "name": "Work-Life Balance",
                "description": "Investigate how people manage their personal and professional lives, making decisions that affect their productivity, happiness, and health.",
                "status": "active",
                "simulations": project_simulations,
            },
        ]
    }
