from evidencemap.models import Paper
from evidencemap.quality_gate import concept_groups, rank_public_papers, split_sentences


def test_split_sentences():
    assert split_sentences('One. Two? Three!') == ['One.', 'Two?', 'Three!']


def test_public_ranking_scores_relevant_paper_first():
    papers = [
        Paper(id='1', title='Unrelated topic', abstract='No matching concepts here.', year=2024, citations=100),
        Paper(
            id='2',
            title='Endometrial organoid implantation model',
            abstract='Endometrial organoids can model embryo implantation and uterine receptivity.',
            year=2025,
            citations=10,
            source='pubmed',
        ),
    ]
    ranked = rank_public_papers('endometrial organoid implantation', papers, limit=2, ranking_mode='recent')
    assert ranked[0].id == '2'
    assert ranked[0].quality_score > 0
    assert 'implantation' in ranked[0].support_sentence.lower()


def test_concept_groups_fallback_for_general_query():
    groups = concept_groups('transparent evidence mapping workflow')
    assert groups
