""""""
import json


class BloomsLO:
    name: str

    _action_verbs: [str]
    _deliverables: [str]
    ...


class KnowledgeLO(BloomsLO):
    '''
    Knowledge involves recognizing or remembering facts, terms, basic concepts, or answers without necessarily understanding what they mean. Some characteristics may include:

    Knowledge of specifics—terminology, specific facts
    Knowledge of ways and means of dealing with specifics—conventions, trends and sequences, classifications and categories
    Knowledge of the universals and abstractions in a field—principles and generalizations, theories and structures

    Example: Name three common varieties of apple.
    '''

    name = "Knowledge"

    _action_verbs = [
        'select', 'list',' name', 'define', 'describe', 'memorize',
        'label', 'identify', 'locate', 'recite', 'state', 'recognize'
    ]

    _deliverables = [
        'events', 'people', 'recordings', 'videos', 'plays', 'filmstrips',
        'radio', 'text readings', 'films', 'newspapers', 'magazines', 'television'
    ]


class ComprehensionLO(BloomsLO):
    '''
    Comprehension involves demonstrating an understanding of facts and ideas by organizing, summarizing, translating, generalizing, giving descriptions, and stating the main ideas.

    Example: Summarize the identifying characteristics of a Golden Delicious apple and a Granny Smith apple.
    '''

    name = "Comprehension"

    _action_verbs = [
        'match', 'restate', 'paraphrase', 'rewrite', 'give examples', 'express', 'illustrate',
        'explain', 'defend', 'distinguish', 'summarize', 'interrelate', 'interpret', 'extend'
    ]

    _deliverables = [
        'recording', 'drama', 'cartoon', 'story', 'speech', 'photograph', 'diagram', 'own statement',
        'model', 'conclusion', 'implication from ieda', 'causal relations', 'analogy', 'outline', 'compare', 'summary'
    ]

class ApplicationLO(BloomsLO):
    '''
    Application involves using acquired knowledge to solve problems in new situations. This involves applying acquired knowledge, facts, techniques and rules. Learners should be able to use prior knowledge to solve problems, identify connections and relationships and how they apply in new situations.

    Example: Would apples prevent scurvy, a disease caused by a deficiency in vitamin C?
    '''

    name = "Application"

    _action_verbs = [
        'organize', 'generalize', 'dramatize', 'prepare', 'produce', 'choose',
        'sketch', 'apply', 'solve', 'draw', 'show', 'paint'
    ]

    _deliverables = [
        'list', 'drama', 'painting', 'sculpture', 'jewelry', 'poetry',
        'illustration', 'solution', 'question', 'follow an outline', 'map', 'project', 'forecast', 'diagram'
    ]


class AnalysisLO(BloomsLO):
    '''
    Analysis involves examining and breaking information into component parts, determining how the parts relate to one another, identifying motives or causes, making inferences, and finding evidence to support generalizations. Its characteristics include:

    Analysis of elements
    Analysis of relationships
    Analysis of organization

	Example: Compare and contrast four ways of serving foods made with apples and examine which ones have the highest health benefits.
    '''

    name = "Analysis"

    _action_verbs = [
        'compare', 'analyze', 'classify', 'point out', 'distinguish', 'categorize',
        'differentiate', 'subdivide', 'infer', 'survey', 'select', 'prioritize'
    ]

    _deliverables = [
        'survey', 'graph', 'syllogism breakdown', 'report',
        'questionnaire', 'argument', 'propaganda', 'word defined', 'statement identified', 'conclusion checked'
    ]


class SynthesisLO(BloomsLO):
    '''
    Synthesis involves building a structure or pattern from diverse elements; it also refers to the act of putting parts together to form a whole or bringing pieces of information together to form a new meaning. Its characteristics include:

    Production of a unique communication
    Production of a plan, or proposed set of operations
    Derivation of a set of abstract relations

	Example: Convert an "unhealthy" recipe for apple pie to a "healthy" recipe by replacing your choice of ingredients. Argue for the health benefits of using the ingredients you chose versus the original ones.
    '''

    name = "Synthesis"

    _action_verbs = [
        'compose', 'originate', 'hypothesize', 'develop', 'design', 'combine',
        'construct', 'produce', 'plan', 'create', 'invent', 'organize'
    ]

    _deliverables = [
        'play', 'experiment', 'alternative action', 'hypothesis', 'formulation', 'book',
        'set of standards', 'game', 'song', 'machine', 'article', 'invention', 'report', 'set of rules'
    ]



class EvaluationLO(BloomsLO):
    '''
    Evaluation involves presenting and defending opinions by making judgments about information, the validity of ideas, or quality of work based on a set of criteria. Its characteristics include:

    Judgments in terms of internal evidence
    Judgments in terms of external criteria

	Example: Which kinds of apples are suitable for baking a pie, and why?
    '''

    name = "Evaluation"

    _action_verbs = [
        'judge', 'relate', 'weight', 'criticize', 'support', 'evaluate',
        'consider', 'critique', 'recommend', 'summarize', 'appraise', 'compare'
    ]

    _deliverables = [
        'conclusion', 'self-evaluation', 'recommendation', 'valuing', 'court trial', 'survey',
        'standard compared', 'standard established', 'discussion', 'assessment'
    ]


class BloomsTaxonomy:
    Knowledge = KnowledgeLO
    Comprehension = ComprehensionLO
    Application = ApplicationLO
    Analysis = AnalysisLO
    Synthesis = SynthesisLO
    Evaluation = EvaluationLO

    def d(self):
        return dict(
            Knowledge=self.Knowledge,
            Comprehension=self.Comprehension,
            Application=self.Application,
            Analysis=self.Analysis,
            Synthesis=self.Synthesis,
            Evaluation=self.Evaluation
        )

def print_actions():
    print(BloomsTaxonomy.Knowledge.name, BloomsTaxonomy.Knowledge._action_verbs)
    print(BloomsTaxonomy.Comprehension.name, BloomsTaxonomy.Comprehension._action_verbs)
    print(BloomsTaxonomy.Application.name, BloomsTaxonomy.Application._action_verbs)
    print(BloomsTaxonomy.Analysis.name, BloomsTaxonomy.Analysis._action_verbs)
    print(BloomsTaxonomy.Synthesis.name, BloomsTaxonomy.Synthesis._action_verbs)
    print(BloomsTaxonomy.Evaluation.name, BloomsTaxonomy.Evaluation._action_verbs)





class LOController:
    def __init__(self, custom_llm_endpoint: str):
        self.blooms = BloomsTaxonomy()

        self.custom_llm_endpoint = custom_llm_endpoint

    def generate_lo(self, stage: str, topic: str, additional_context: str = None, number_of_suggestions: int = 3):
        import requests
        import random

        if stage not in self.blooms.d():
            print(f"Invalid stage: {stage}", self.blooms.d())
            raise ValueError(f"Invalid stage: {stage}")

        lo = self.blooms.d()[stage]()

        los = []

        for i in range(number_of_suggestions):
            if i % 2 == 0:
                action_verb = random.choice(lo._action_verbs)
                deliverable = None
            else:
                deliverable = random.choice(lo._deliverables)
                action_verb = None

            suggested = requests.post(
                self.custom_llm_endpoint, data=dict(
                chat_function='generate_lo',
                custom_data=json.dumps(dict(
                    stage=stage,
                    topic=topic,
                    action_verb=action_verb if action_verb else '',
                    deliverable=deliverable if deliverable else '',
                    additional_context=additional_context if additional_context else ''
                )))
            )

            print(type(suggested), suggested.text)

            # Structure should look like this: lo, suggested_assignment = suggested.json()['lo'], suggested.json()['suggested_assignment']
            los.append(
                suggested.json()
            )

        return los



LO_PROMPT = 'You are a helpful tutor on all topics. You are helping a student generate a learning objective for a lesson. The student is asking you to use Bloom\'s Taxonomy to generate a learning objective for a specific stage and topic. The student has will ask you to generate a learning objective for a particular taxonomy stage and a specific topic'
LO_PROMPT += 'You are to provide only the learning objective and no context or explanation prior to it, as the learning objective will be added directly to the lesson plan.'



def lo_chat(stage: str, topic: str) -> str:
    if stage.lower() not in [stg.lower() for stg in BloomsTaxonomy().d().keys()]:
        raise ValueError(f"Invalid stage: {stage}")

    message = f"Using Bloom's Taxonomy, generate a learning objective for {stage} stage, {topic} topic"

    from lib.completions.main import Completions
    from settings import GPT_MODEL_ID

    assistant_message = Completions(model=GPT_MODEL_ID, system_prompt=LO_PROMPT).complete(message)
    return assistant_message


def test():
    from settings import BLOOMS_LLM_ENDPOINT
    lo_controller = LOController(BLOOMS_LLM_ENDPOINT)
    print(lo_controller.generate_lo('Knowledge', 'Apples', 'Apple pie', 3))
