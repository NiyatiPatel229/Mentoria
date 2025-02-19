import PyPDF2
import nltk
import spacy
import random
from nltk.corpus import wordnet
from nltk.tokenize import sent_tokenize, word_tokenize
import re
import pprint
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from collections import defaultdict
from datetime import datetime


class QuestionPaperGenerator:
    def __init__(self):
        self.content = ""
        self.sentences = []
        self.questions = []
        self.key_concepts = defaultdict(list)
        self.nlp = spacy.load('en_core_web_sm')
        self.key_terms = {}
        
    def extract_text_from_pdf(self, pdf_path):
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    self.content += page.extract_text()
            self.sentences = sent_tokenize(self.content)
            self.doc = self.nlp(self.content)
            self._extract_key_concepts()
            self._extract_key_terms()
            return True
        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
            return False

    def _extract_key_terms(self):
        """Extract key terms for MCQs"""
        for sent in self.doc.sents:
            definition_patterns = [
                r'(?P<term>[A-Z][^.]*?) (?:is|are|refers to|means) (?P<definition>[^.]*\.)',
                r'(?P<term>[A-Z][^.]*?): (?P<definition>[^.]*\.)',
                r'(?P<definition>[^.]*?) is called (?P<term>[^.]*\.)',
            ]
            
            for pattern in definition_patterns:
                matches = re.finditer(pattern, sent.text)
                for match in matches:
                    term = match.group('term').strip()
                    definition = match.group('definition').strip()
                    
                    if term not in self.key_terms:
                        self.key_terms[term] = {
                            'definition': definition,
                            'examples': [],
                            'related_terms': [],
                            'context': []
                        }
            
            for term in self.key_terms:
                if term.lower() in sent.text.lower():
                    self.key_terms[term]['context'].append(sent.text)
                    for chunk in sent.noun_chunks:
                        if chunk.text.lower() != term.lower():
                            self.key_terms[term]['related_terms'].append(chunk.text)

    def _extract_key_concepts(self):
        """Extract key concepts for descriptive and scenario questions"""
        doc = self.nlp(self.content)
        
        for ent in doc.ents:
            self.key_concepts[ent.label_].append({
                'text': ent.text,
                'context': ent.sent.text
            })
        
        for sent in doc.sents:
            for chunk in sent.noun_chunks:
                if len(chunk.text.split()) > 1:
                    self.key_concepts['CONCEPT'].append({
                        'text': chunk.text,
                        'context': sent.text
                    })

    def generate_mcq_distractors(self, correct_answer, term_info):
        """Generate meaningful distractors for MCQs"""
        distractors = set()
        
        # Use related terms
        distractors.update(term_info['related_terms'][:2])
        
        # Use WordNet
        synsets = wordnet.synsets(correct_answer)
        if synsets:
            for syn in synsets:
                distractors.update([lemma.name() for lemma in syn.lemmas()][:2])
                for hypernym in syn.hypernyms():
                    distractors.update([lemma.name() for lemma in hypernym.lemmas()][:1])
        
        # Use similar terms from document
        doc_terms = [ent.text for ent in self.doc.ents if ent.label_ in ['ORG', 'PRODUCT', 'TECH']]
        if doc_terms:
            distractors.update(random.sample(doc_terms, min(2, len(doc_terms))))
        
        # Clean distractors
        distractors = [d for d in distractors 
                      if d.lower() != correct_answer.lower() 
                      and len(d) > 2 
                      and not d.isnumeric()]
        
        if len(distractors) < 3:
            words = word_tokenize(term_info['definition'])
            key_words = [word for word, pos in nltk.pos_tag(words) 
                        if pos.startswith(('NN', 'VB', 'JJ')) 
                        and word.lower() != correct_answer.lower()]
            if key_words:
                distractors.extend(random.sample(key_words, min(3 - len(distractors), len(key_words))))
        
        return list(set(distractors))[:3]

    def generate_mcq(self):
        """Generate a single MCQ"""
        if not self.key_terms:
            return None
            
        term, term_info = random.choice(list(self.key_terms.items()))
        
        templates = [
            f"What is {term}?",
            f"Which of the following best defines {term}?",
            f"What is the correct description of {term}?",
            f"Which statement correctly explains {term}?",
            f"The term '{term}' refers to:",
        ]
        
        question = random.choice(templates)
        correct_answer = term_info['definition']
        
        distractors = self.generate_mcq_distractors(term, term_info)
        options = [correct_answer] + distractors
        random.shuffle(options)
        
        return {
            'question': question,
            'options': options,
            'correct_answer': options.index(correct_answer)
        }

    def generate_descriptive_question(self, marks):
        """Generate descriptive questions"""
        templates = {
            'short': [
                "Define {} and give an example.",
                "What are the key features of {}?",
                "Explain the significance of {} in brief.",
                "How does {} contribute to the field?",
                "Write short notes on {}."
            ],
            'medium': [
                "Explain the relationship between {} and {} with examples.",
                "Describe the process of {} and its applications.",
                "What are the advantages and disadvantages of {}?",
                "How does {} impact {}? Explain with examples.",
                "Analyze the role of {} in {}."
            ],
            'long': [
                "Critically evaluate the importance of {} in relation to {}. Support your answer with examples.",
                "Compare and contrast {} with {}. Provide detailed analysis.",
                "Discuss the evolution of {} and its current relevance in {}.",
                "'{}' has revolutionized '{}'. Justify this statement with examples.",
                "Analyze the challenges and opportunities associated with {} in the context of {}."
            ]
        }
        
        concepts = random.sample(self.key_concepts['CONCEPT'], min(2, len(self.key_concepts['CONCEPT'])))
        
        if marks <= 2:
            template = random.choice(templates['short'])
            question = template.format(concepts[0]['text'])
        elif marks <= 5:
            template = random.choice(templates['medium'])
            question = template.format(concepts[0]['text'], 
                                    concepts[1]['text'] if len(concepts) > 1 else "your field")
        else:
            template = random.choice(templates['long'])
            question = template.format(concepts[0]['text'], 
                                    concepts[1]['text'] if len(concepts) > 1 else "modern applications")
        
        return question

    def generate_scenario_based(self):
        """Generate scenario-based questions"""
        if not self.key_concepts['CONCEPT']:
            return None
        
        concepts = random.sample(self.key_concepts['CONCEPT'], 
                               min(2, len(self.key_concepts['CONCEPT'])))
        
        scenario_templates = [
            "In a recent project, a team was working with {} when they encountered challenges related to {}. ",
            "A company implementing {} found that it significantly affected their {}. ",
            "While developing a new system using {}, researchers discovered an interesting connection with {}. "
        ]
        
        question_templates = [
            "Analyze this situation and propose a solution using relevant concepts.",
            "What are the key challenges in this scenario and how would you address them?",
            "How would you apply theoretical concepts to resolve this situation?",
            "Evaluate the scenario and suggest improvements.",
            "What alternative approaches could be used in this situation?"
        ]
        
        scenario = random.choice(scenario_templates).format(
            concepts[0]['text'],
            concepts[1]['text'] if len(concepts) > 1 else "related systems"
        )
        scenario += concepts[0]['context'] + " "
        if len(concepts) > 1:
            scenario += concepts[1]['context']
        
        return {
            'scenario': scenario,
            'question': random.choice(question_templates)
        }

    def generate_questions(self, question_config):
        """Generate all types of questions"""
        if 'mcq' in question_config:
            for _ in range(question_config['mcq']['count']):
                mcq = self.generate_mcq()
                if mcq:
                    mcq['type'] = 'mcq'
                    mcq['marks'] = question_config['mcq']['marks']
                    self.questions.append(mcq)
        
        if 'descriptive' in question_config:
            for _ in range(question_config['descriptive']['count']):
                question = self.generate_descriptive_question(
                    question_config['descriptive']['marks']
                )
                if question:
                    self.questions.append({
                        'type': 'descriptive',
                        'question': question,
                        'marks': question_config['descriptive']['marks']
                    })
        
        if 'scenario' in question_config:
            for _ in range(question_config['scenario']['count']):
                scenario_q = self.generate_scenario_based()
                if scenario_q:
                    scenario_q['type'] = 'scenario'
                    scenario_q['marks'] = question_config['scenario']['marks']
                    self.questions.append(scenario_q)
    
    

class EnhancedQuestionPaperGenerator(QuestionPaperGenerator):
    def __init__(self):
        super().__init__()
        self.answers = []

    def generate_mcq(self):
        mcq = super().generate_mcq()
        if mcq:
            correct_option = chr(97 + mcq['correct_answer'])
            explanation = f"The correct answer is option {correct_option}. {mcq['options'][mcq['correct_answer']]}"
            mcq['answer'] = explanation
        return mcq

    def generate_descriptive_question(self, marks):
        question = super().generate_descriptive_question(marks)
        if question:
            relevant_concepts = [concept for concept in self.key_concepts['CONCEPT'] 
                              if any(term in question.lower() for term in concept['text'].lower().split())]
            
            answer = ""
            if relevant_concepts:
                concept_count = min(marks // 2, len(relevant_concepts))
                for concept in relevant_concepts[:concept_count]:
                    answer += f"{concept['context']}\n\n"
                    related_terms = [term for term in self.key_terms 
                                   if term.lower() in concept['context'].lower()]
                    for term in related_terms[:marks]:
                        answer += f"• {term}: {self.key_terms[term]['definition']}\n"
            
            # Return both question and answer in the structure
            return {
                'question': question,
                'answer': answer if answer else "See detailed solution in answer key."
            }
        return None

    def generate_scenario_based(self):
        scenario = super().generate_scenario_based()
        if scenario:
            concepts_mentioned = []
            for concept in self.key_concepts['CONCEPT']:
                if concept['text'].lower() in scenario['scenario'].lower():
                    concepts_mentioned.append(concept)
            
            answer = "Suggested Solution:\n\n"
            if concepts_mentioned:
                answer += "1. Analysis of the Situation:\n"
                for concept in concepts_mentioned:
                    answer += f"   • {concept['context']}\n"
                
                answer += "\n2. Proposed Solutions:\n"
                related_terms = []
                for concept in concepts_mentioned:
                    for term in self.key_terms:
                        if term.lower() in concept['context'].lower():
                            related_terms.append(term)
                
                for term in related_terms[:3]:
                    answer += f"   • Apply {term}: {self.key_terms[term]['definition']}\n"
            
            scenario['answer'] = answer if answer else "See detailed solution in answer key."
            return scenario
        return None

    def generate_questions(self, question_config):
        """Generate questions with multiple mark categories"""
        # Handle MCQs
        if 'mcq' in question_config:
            for mark_category in question_config['mcq']:
                for _ in range(mark_category['count']):
                    mcq = self.generate_mcq()
                    if mcq:
                        mcq['type'] = 'mcq'
                        mcq['marks'] = mark_category['marks']
                        self.questions.append(mcq)
        
        # Handle descriptive questions
        if 'descriptive' in question_config:
            for mark_category in question_config['descriptive']:
                for _ in range(mark_category['count']):
                    question_data = self.generate_descriptive_question(mark_category['marks'])
                    if question_data:
                        self.questions.append({
                            'type': 'descriptive',
                            'question': question_data['question'],
                            'answer': question_data['answer'],  # Make sure answer is included
                            'marks': mark_category['marks']
                        })
        
        # Handle scenario questions
        if 'scenario' in question_config:
            for mark_category in question_config['scenario']:
                for _ in range(mark_category['count']):
                    scenario_q = self.generate_scenario_based()
                    if scenario_q:
                        scenario_q['type'] = 'scenario'
                        scenario_q['marks'] = mark_category['marks']
                        if 'answer' not in scenario_q:  # Add default answer if missing
                            scenario_q['answer'] = "See detailed solution in answer key."
                        self.questions.append(scenario_q)

    # ... rest of the methods (export_to_pdf and export_answer_key) remain the same ...

# Previous code remains the same...
    def export_to_pdf(self, output_path):
        """Export question paper to PDF with mark categories"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = getSampleStyleSheet()
        
        # Add all required custom styles
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        # Add the missing QuestionStyle
        styles.add(ParagraphStyle(
            name='QuestionStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            leftIndent=20,
            leading=14
        ))

        # Add other custom styles
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            spaceBefore=20,
            textColor=colors.HexColor('#2E5090')
        ))

        styles.add(ParagraphStyle(
            name='MarkCategory',
            parent=styles['Normal'],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=6,
            textColor=colors.HexColor('#444444'),
            fontName='Helvetica-Bold'
        ))
        
        content = []
        
        # Header
        content.append(Paragraph("QUESTION PAPER", styles['CustomTitle']))
        content.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        
        # Calculate total marks
        total_marks = sum(q['marks'] for q in self.questions)
        content.append(Paragraph(f"Total Marks: {total_marks}", styles['Normal']))
        content.append(Paragraph(f"Time: {total_marks * 1.5} minutes", styles['Normal']))
        content.append(Spacer(1, 20))
        
        # Group questions by type and marks
        def group_questions():
            grouped = defaultdict(lambda: defaultdict(list))
            for q in self.questions:
                grouped[q['type']][q['marks']].append(q)
            return grouped
        
        grouped_questions = group_questions()
        
        # MCQs
        if 'mcq' in grouped_questions:
            content.append(Paragraph("Section A: Multiple Choice Questions", styles['SectionHeader']))
            content.append(Spacer(1, 12))
            
            question_num = 1
            for marks, questions in sorted(grouped_questions['mcq'].items()):
                if questions:
                    content.append(Paragraph(f"{marks} Mark Questions:", styles['MarkCategory']))
                    content.append(Spacer(1, 6))
                    
                    for q in questions:
                        content.append(Paragraph(
                            f"{question_num}. {q['question']} [{marks} mark{'s' if marks > 1 else ''}]", 
                            styles['QuestionStyle']
                        ))
                        options = []
                        for j, option in enumerate(q['options']):
                            options.append(ListItem(
                                Paragraph(f"{chr(97+j)}) {option}", styles['Normal'])
                            ))
                        content.append(ListFlowable(options, bulletType='bullet', leftIndent=50))
                        content.append(Spacer(1, 12))
                        question_num += 1
        
        # Descriptive Questions
        if 'descriptive' in grouped_questions:
            content.append(Paragraph("Section B: Descriptive Questions", styles['SectionHeader']))
            content.append(Spacer(1, 12))
            
            question_num = 1
            for marks, questions in sorted(grouped_questions['descriptive'].items()):
                if questions:
                    content.append(Paragraph(f"{marks} Mark Questions:", styles['MarkCategory']))
                    content.append(Spacer(1, 6))
                    
                    for q in questions:
                        content.append(Paragraph(
                            f"{question_num}. {q['question']} [{marks} marks]",
                            styles['QuestionStyle']
                        ))
                        content.append(Spacer(1, 12))
                        question_num += 1
        
        # Scenario Questions
        if 'scenario' in grouped_questions:
            content.append(Paragraph("Section C: Scenario-based Questions", styles['SectionHeader']))
            content.append(Spacer(1, 12))
            
            question_num = 1
            for marks, questions in sorted(grouped_questions['scenario'].items()):
                if questions:
                    content.append(Paragraph(f"{marks} Mark Questions:", styles['MarkCategory']))
                    content.append(Spacer(1, 6))
                    
                    for q in questions:
                        content.append(Paragraph(f"{question_num}. Read the following scenario:", styles['QuestionStyle']))
                        content.append(Paragraph(q['scenario'], styles['Normal']))
                        content.append(Spacer(1, 6))
                        content.append(Paragraph(
                            f"Question: {q['question']} [{marks} marks]",
                            styles['QuestionStyle']
                        ))
                        content.append(Spacer(1, 12))
                        question_num += 1
        
        doc.build(content)
        
    def export_answer_key(self, output_path):
        """Export answer key to PDF with improved formatting"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = getSampleStyleSheet()
        
        # Define styles for answer key
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            spaceBefore=20,
            textColor=colors.HexColor('#2E5090')
        ))
        
        styles.add(ParagraphStyle(
            name='QuestionHeader',
            parent=styles['Normal'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#000000'),
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='AnswerText',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=15,
            leftIndent=20,
            leading=16
        ))

        styles.add(ParagraphStyle(
            name='MarkCategory',
            parent=styles['Normal'],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=6,
            textColor=colors.HexColor('#444444'),
            fontName='Helvetica-Bold'
        ))
        
        content = []
        
        # Header
        content.append(Paragraph("ANSWER KEY", styles['CustomTitle']))
        content.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        content.append(Spacer(1, 20))
        
        # Group questions by type and marks
        def group_questions():
            grouped = defaultdict(lambda: defaultdict(list))
            for q in self.questions:
                grouped[q['type']][q['marks']].append(q)
            return grouped
        
        grouped_questions = group_questions()
        
        # MCQ Answers
        if 'mcq' in grouped_questions:
            content.append(Paragraph("Section A: Multiple Choice Questions", styles['SectionHeader']))
            
            question_num = 1
            for marks, questions in sorted(grouped_questions['mcq'].items()):
                if questions:
                    content.append(Paragraph(f"{marks} Mark Questions:", styles['MarkCategory']))
                    content.append(Spacer(1, 6))
                    
                    for q in questions:
                        content.append(Paragraph(
                            f"Question {question_num}: {q['question']}", 
                            styles['QuestionHeader']
                        ))
                        content.append(Paragraph(q['answer'], styles['AnswerText']))
                        content.append(Spacer(1, 10))
                        question_num += 1
        
        # Descriptive Answers
        if 'descriptive' in grouped_questions:
            content.append(Paragraph("Section B: Descriptive Questions", styles['SectionHeader']))
            
            question_num = 1
            for marks, questions in sorted(grouped_questions['descriptive'].items()):
                if questions:
                    content.append(Paragraph(f"{marks} Mark Questions:", styles['MarkCategory']))
                    content.append(Spacer(1, 6))
                    
                    for q in questions:
                        content.append(Paragraph(
                            f"Question {question_num}: {q['question']}", 
                            styles['QuestionHeader']
                        ))
                        content.append(Paragraph(
                            q['answer'].replace('\n', '<br/>'),
                            styles['AnswerText']
                        ))
                        content.append(Spacer(1, 15))
                        question_num += 1
        
        # Scenario Answers
        if 'scenario' in grouped_questions:
            content.append(Paragraph("Section C: Scenario-based Questions", styles['SectionHeader']))
            
            question_num = 1
            for marks, questions in sorted(grouped_questions['scenario'].items()):
                if questions:
                    content.append(Paragraph(f"{marks} Mark Questions:", styles['MarkCategory']))
                    content.append(Spacer(1, 6))
                    
                    for q in questions:
                        content.append(Paragraph(
                            f"Question {question_num}:", 
                            styles['QuestionHeader']
                        ))
                        content.append(Paragraph(
                            f"Scenario: {q['scenario']}", 
                            styles['QuestionHeader']
                        ))
                        content.append(Paragraph(
                            f"Question: {q['question']}", 
                            styles['QuestionHeader']
                        ))
                        content.append(Paragraph(
                            q['answer'].replace('\n', '<br/>'), 
                            styles['AnswerText']
                        ))
                        content.append(Spacer(1, 15))
                        question_num += 1
        
        doc.build(content)

# Rest of the code remains the same...

def generate_question_paper_with_answers(pdf_path, question_config, output_pdf_path, answer_key_path):
    """Main function to generate question paper and answer key"""
    generator = EnhancedQuestionPaperGenerator()
    if generator.extract_text_from_pdf(pdf_path):
        generator.generate_questions(question_config)
        generator.export_to_pdf(output_pdf_path)
        generator.export_answer_key(answer_key_path)
        return True
    return False

config = {
    'mcq': [
        {'marks': 1, 'count': 5},
    ],
    'descriptive': [
        {'marks': 3, 'count': 2},
        {'marks': 5, 'count': 1}
    ],
    'scenario': [
        {'marks': 5, 'count': 1},
    ]
}

# generate_question_paper_with_answers(
#     r'C:\Users\patel\Documents\odoo\Mentoria\sample-q1.pdf',
#     config,
#     r'C:\Users\patel\Documents\odoo\Mentoria\backend\qreports\question_paper.pdf',
#     r'C:\Users\patel\Documents\odoo\Mentoria\backend\qreports\answer_key.pdf'
# )

# question_paper.py modifications
def generate_question_paper_with_answers(pdf_path, config, output_pdf_path, answer_key_path):
    print(f"\nProcessing PDF: {pdf_path}")
    print("Final Config Structure:")
    pprint.pprint({
        'mcq': [{'marks': m['marks'], 'count': m['count']} for m in config['mcq']],
        'descriptive': [{'marks': m['marks'], 'count': m['count']} for m in config['descriptive']],
        'scenario': [{'marks': m['marks'], 'count': m['count']} for m in config['scenario']]
    })
    
    generator = EnhancedQuestionPaperGenerator()
    if generator.extract_text_from_pdf(pdf_path):
        generator.generate_questions({
            'mcq': config['mcq'],
            'descriptive': config['descriptive'],
            'scenario': config['scenario']
        })
        generator.export_to_pdf(output_pdf_path)
        generator.export_answer_key(answer_key_path)
        return True
    return False
