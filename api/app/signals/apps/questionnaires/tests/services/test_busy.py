# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2021 Gemeente Amsterdam
from django.test import TestCase
from networkx import MultiDiGraph

from signals.apps.questionnaires.factories import AnswerFactory, ChoiceFactory, SessionFactory
from signals.apps.questionnaires.models import Answer, Edge
from signals.apps.questionnaires.services.busy import QuestionGraphService
from signals.apps.questionnaires.tests.test_models import create_diamond_plus


class TestQuestionGraphService(TestCase):
    def test_get_edges(self):
        q_graph = create_diamond_plus()
        session = SessionFactory.create(questionnaire__graph=q_graph)
        service = QuestionGraphService(session)

        edges = service._get_edges(q_graph)
        self.assertEqual(len(edges), 6)

    def test_build_nx_graph_no_choices_predefined(self):
        q_graph = create_diamond_plus()
        session = SessionFactory.create(questionnaire__graph=q_graph)
        service = QuestionGraphService(session)
        edges = service._get_edges(q_graph)

        nx_graph = service._build_nx_graph(edges, q_graph.first_question)
        self.assertIsInstance(nx_graph, MultiDiGraph)
        self.assertEqual(len(nx_graph.nodes), 7)

    def test_get_all_questions(self):
        q_graph = create_diamond_plus()
        session = SessionFactory.create(questionnaire__graph=q_graph)
        service = QuestionGraphService(session)
        edges = service._get_edges(q_graph)
        nx_graph = service._build_nx_graph(edges, q_graph.first_question)

        questions = service._get_all_questions(nx_graph)
        self.assertEqual(len(questions), 7)
        self.assertEqual({q.analysis_key for q in questions}, set(f'q{n}' for n in range(1, 8)))

    def test_get_reachable_questions(self):
        q_graph = create_diamond_plus()
        session = SessionFactory.create(questionnaire__graph=q_graph)
        service = QuestionGraphService(session)
        edges = service._get_edges(q_graph)
        nx_graph = service._build_nx_graph(edges, q_graph.first_question)

        questions = service.get_reachable_questions(nx_graph, q_graph.first_question)
        self.assertEqual(len(questions), 5)
        self.assertEqual({q.analysis_key for q in questions}, set(f'q{n}' for n in range(1, 6)))

    def test_load_path_independent_data_no_answers(self):
        q_graph = create_diamond_plus()
        session = SessionFactory.create(questionnaire__graph=q_graph)
        service = QuestionGraphService(session)

        service._load_path_independent_data(session)
        self.assertEqual(len(service.edges), 6)
        self.assertIsInstance(service.nx_graph, MultiDiGraph)
        self.assertEqual(len(service.nx_graph.nodes), 7)
        self.assertEqual(len(service.questions), 7)
        self.assertEqual(len(service.answers), 0)
        self.assertEqual(len(service.questions_by_id), 7)

    # -- below tests for path dependence --

    def test_get_all_answers(self):
        q_graph = create_diamond_plus()
        session = SessionFactory.create(questionnaire__graph=q_graph)
        service = QuestionGraphService(session)
        service._load_path_independent_data(session)

        for q in service.questions:
            AnswerFactory.create(session=session, question=q, payload='answer')

        service._load_path_independent_data(session)
        self.assertEqual(len(service.answers), 7)
        self.assertEqual(len(service.questions_by_id), 7)
        self.assertEqual(len(service.answers_by_question_id), 7)

    def test_get_next_question_no_choices_predefined(self):
        q_graph = create_diamond_plus()
        session = SessionFactory.create(questionnaire__graph=q_graph)
        service = QuestionGraphService(session)
        service._load_path_independent_data(session)

        # First question in "diamond_plus" QuestionGraph is a decision point,
        # the create_diamond_plus function does not set choices or edge order
        # explicitly. We test the decision point here by answering the first
        # question, determining the next question and reordering the edges
        # and checking we get the other branch.
        a = Answer.objects.create(session=session, question=q_graph.first_question, payload='answer')
        next_question_1 = service._get_next_question(
            service.nx_graph,
            service.questions_by_id,
            q_graph.first_question,
            a.payload
        )

        # First set order to the old order, nothing should change.
        edge_ids_before = q_graph.get_edge_order(q_graph.first_question)
        edge_ids_after = q_graph.set_edge_order(q_graph.first_question, edge_ids_before)
        service._load_path_independent_data(session)  # reload, because cache is now stale

        self.assertEqual(list(edge_ids_before), list(edge_ids_after))
        next_question_2 = service._get_next_question(
            service.nx_graph,
            service.questions_by_id,
            q_graph.first_question,
            a.payload
        )
        self.assertEqual(next_question_1.id, next_question_2.id)  # nothing should change

        # Now change the order of outgoing edges from q_graph.first_question
        edge_ids_before = q_graph.get_edge_order(q_graph.first_question)
        new_order = list(reversed(edge_ids_before))
        edge_ids_after = q_graph.set_edge_order(q_graph.first_question, new_order)
        self.assertNotEqual(list(edge_ids_after), list(edge_ids_before))
        service._load_path_independent_data(session)  # reload, because cache is now stale

        self.assertEqual(list(edge_ids_after), list(new_order))
        next_question_3 = service._get_next_question(
            service.nx_graph,
            service.questions_by_id,
            q_graph.first_question,
            a.payload
        )
        self.assertNotEqual(next_question_1.id, next_question_3.id)  # should have changed

    def test_get_next_question_with_choices_predefined(self):
        # Update QuestionGraph with predefined choices
        c2 = ChoiceFactory.create(payload='q2')
        c3 = ChoiceFactory.create(payload='q3')

        q_graph = create_diamond_plus()
        edge_to_q2 = Edge.objects.filter(
            question=q_graph.first_question, graph=q_graph, next_question__analysis_key='q2')
        edge_to_q3 = Edge.objects.filter(
            question=q_graph.first_question, graph=q_graph, next_question__analysis_key='q3')

        self.assertEqual(edge_to_q2.count(), 1)
        self.assertEqual(edge_to_q3.count(), 1)

        edge_to_q2.update(choice=c2)
        edge_to_q3.update(choice=c3)

        # ---
        session = SessionFactory.create(questionnaire__graph=q_graph)
        service = QuestionGraphService(session)
        service._load_path_independent_data(session)

        a1 = Answer.objects.create(
            session=session,
            question=q_graph.first_question,
            payload='NOT A PREDEFINED CHOICE',
        )
        next_question_1 = service._get_next_question(
            service.nx_graph,
            service.questions_by_id,
            q_graph.first_question,
            a1.payload
        )
        self.assertIsNone(next_question_1)

        a2 = Answer.objects.create(
            session=session,
            question=q_graph.first_question,
            payload='q2'
        )
        next_question_2 = service._get_next_question(
            service.nx_graph,
            service.questions_by_id,
            q_graph.first_question,
            a2.payload
        )
        self.assertEqual(next_question_2.analysis_key, 'q2')

        a3 = Answer.objects.create(
            session=session,
            question=q_graph.first_question,
            payload='q3'
        )
        next_question_3 = service._get_next_question(
            service.nx_graph,
            service.questions_by_id,
            q_graph.first_question,
            a3.payload
        )
        self.assertEqual(next_question_3.analysis_key, 'q3')

    def test_get_reachable_questions_answers_no_answers(self):
        q_graph = create_diamond_plus()
        session = SessionFactory.create(questionnaire__graph=q_graph)
        service = QuestionGraphService(session)

        service._load_path_independent_data(session)
        questions_by_id, unanswered_by_id, answers_by_id = service._get_reachable_questions_and_answers(
            service.nx_graph, service.questions_by_id, service.answers_by_question_id)

        self.assertEqual(len(questions_by_id), 4)  # should only return questions on one branch
        self.assertEqual(len(unanswered_by_id), 4)  # should only return questions on one branch
        self.assertEqual(len(answers_by_id), 0)  # no answers yet

    def test_get_reachable_questions_answers_one_answer(self):
        q_graph = create_diamond_plus()
        session = SessionFactory.create(questionnaire__graph=q_graph)
        service = QuestionGraphService(session)

        # get references to questions
        service._load_path_independent_data(session)
        q_by_analysis_key = {q.analysis_key: q for q in service.questions}

        # Answer questions
        Answer.objects.create(
            session=session,
            question=q_by_analysis_key['q1'],
            payload='q1'
        )

        service._load_path_independent_data(session)
        questions_by_id, unanswered_by_id, answers_by_id = service._get_reachable_questions_and_answers(
            service.nx_graph, service.questions_by_id, service.answers_by_question_id)

        self.assertEqual(len(questions_by_id), 4)  # should only return questions on one branch
        self.assertEqual(len(unanswered_by_id), 3)
        self.assertEqual(len(answers_by_id), 1)  # one question answered

    def test_get_reachable_questions_answers_one_path(self):
        q_graph = create_diamond_plus()
        session = SessionFactory.create(questionnaire__graph=q_graph)
        service = QuestionGraphService(session)

        # get references to questions
        service._load_path_independent_data(session)
        q_by_analysis_key = {q.analysis_key: q for q in service.questions}

        # Answer questions
        Answer.objects.create(
            session=session,
            question=q_by_analysis_key['q1'],
            payload='q1'
        )
        Answer.objects.create(
            session=session,
            question=q_by_analysis_key['q2'],
            payload='q2'
        )
        Answer.objects.create(
            session=session,
            question=q_by_analysis_key['q4'],
            payload='q4'
        )
        Answer.objects.create(
            session=session,
            question=q_by_analysis_key['q5'],
            payload='q5'
        )

        service._load_path_independent_data(session)
        questions_by_id, unanswered_by_id, answers_by_id = service._get_reachable_questions_and_answers(
            service.nx_graph, service.questions_by_id, service.answers_by_question_id)

        self.assertEqual(len(questions_by_id), 4)  # should only return questions on one branch
        self.assertEqual(len(unanswered_by_id), 0)
        self.assertEqual(len(answers_by_id), 4)  # all questions answered

    def test_get_answers_by_analysis_key_no_answer(self):
        q_graph = create_diamond_plus()
        session = SessionFactory.create(questionnaire__graph=q_graph)
        service = QuestionGraphService(session)

        service._load_path_independent_data(session)
        service._load_path_dependent_data(session)
        answers_by_analysis_key = service.get_answers_by_analysis_key()

        self.assertEqual(answers_by_analysis_key, dict())

    def test_get_answers_by_analysis_key_one_answer(self):
        q_graph = create_diamond_plus()
        session = SessionFactory.create(questionnaire__graph=q_graph)
        service = QuestionGraphService(session)

        service._load_path_independent_data(session)
        q_by_analysis_key = {q.analysis_key: q for q in service.questions}

        # Answer questions
        Answer.objects.create(
            session=session,
            question=q_by_analysis_key['q1'],
            payload='q1'
        )
        service._load_path_independent_data(session)
        service._load_path_dependent_data(session)
        answers_by_analysis_key = service.get_answers_by_analysis_key()

        self.assertEqual(len(answers_by_analysis_key), 1)
        self.assertIn('q1', answers_by_analysis_key)
        self.assertEqual(answers_by_analysis_key['q1'].payload, 'q1')

    def test_get_answers_by_analysis_key_one_path(self):
        q_graph = create_diamond_plus()
        session = SessionFactory.create(questionnaire__graph=q_graph)
        service = QuestionGraphService(session)

        # get references to questions
        service._load_path_independent_data(session)
        q_by_analysis_key = {q.analysis_key: q for q in service.questions}

        # Answer questions
        Answer.objects.create(
            session=session,
            question=q_by_analysis_key['q1'],
            payload='q1'
        )
        Answer.objects.create(
            session=session,
            question=q_by_analysis_key['q2'],
            payload='q2'
        )
        Answer.objects.create(
            session=session,
            question=q_by_analysis_key['q4'],
            payload='q4'
        )
        Answer.objects.create(
            session=session,
            question=q_by_analysis_key['q5'],
            payload='q5'
        )

        service._load_path_independent_data(session)
        service._load_path_dependent_data(session)
        answers_by_analysis_key = service.get_answers_by_analysis_key()

        self.assertEqual(len(answers_by_analysis_key), 4)
        for key in ['q1', 'q2', 'q4', 'q5']:
            self.assertEqual(answers_by_analysis_key[key].payload, key)

    def test_get_extra_properties_no_answers(self):
        q_graph = create_diamond_plus()
        session = SessionFactory.create(questionnaire__graph=q_graph)
        service = QuestionGraphService(session)

        service._load_path_independent_data(session)
        service._load_path_dependent_data(session)
        extra_properties = service.get_extra_properties('URL')

        self.assertEqual(extra_properties, [])

    def test_get_extra_properties_one_answer(self):
        q_graph = create_diamond_plus()
        session = SessionFactory.create(questionnaire__graph=q_graph)
        service = QuestionGraphService(session)

        service._load_path_independent_data(session)
        q_by_analysis_key = {q.analysis_key: q for q in service.questions}

        # Answer questions
        Answer.objects.create(
            session=session,
            question=q_by_analysis_key['q1'],
            payload='q1'
        )
        service._load_path_independent_data(session)
        service._load_path_dependent_data(session)
        extra_properties = service.get_extra_properties('URL')

        self.assertEqual(len(extra_properties), 1)
        self.assertEqual(extra_properties[0]['category_url'], 'URL')
        self.assertEqual(extra_properties[0]['label'], q_by_analysis_key['q1'].short_label)

    def test_get_extra_properties_one_path(self):
        q_graph = create_diamond_plus()
        session = SessionFactory.create(questionnaire__graph=q_graph)
        service = QuestionGraphService(session)

        # get references to questions
        service._load_path_independent_data(session)
        q_by_analysis_key = {q.analysis_key: q for q in service.questions}

        # Answer questions
        Answer.objects.create(
            session=session,
            question=q_by_analysis_key['q1'],
            payload='q1'
        )
        Answer.objects.create(
            session=session,
            question=q_by_analysis_key['q2'],
            payload='q2'
        )
        Answer.objects.create(
            session=session,
            question=q_by_analysis_key['q4'],
            payload='q4'
        )
        Answer.objects.create(
            session=session,
            question=q_by_analysis_key['q5'],
            payload='q5'
        )

        service._load_path_independent_data(session)
        service._load_path_dependent_data(session)
        extra_properties = service.get_extra_properties('URL')

        self.assertEqual(len(extra_properties), 4)
