import sys 
import re

from sirji.messages.problem_statement import ProblemStatementMessage
from sirji.messages.answer import AnswerMessage
from sirji.messages.feedback import FeedbackMessage
from sirji.messages.acknowledge import AcknowledgeMessage
from sirji.prompts.user import UserPrompt
from sirji.messages.parser import MessageParser

from sirji.storage.steps import get_steps
from sirji.tools.logger import planner as pLogger

class SingletonMeta(type):
    """
    This is a metaclass that will be used to create a Singleton class.
    It ensures that only one instance of the Singleton class exists.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        # If an instance of the class does not exist, create one; otherwise, return the existing one.
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class User(metaclass=SingletonMeta):
    def generate_problem_statement_message(self, problem_statement, for_user):
        user = UserPrompt(for_user, '')
        problem_statement_message = ProblemStatementMessage(for_user)

        return problem_statement_message.generate(user.name(), {
            "details": problem_statement
        })

    def generate_answer_message(self, answer, for_user):  
        user = UserPrompt(for_user, '')
        answer_message = AnswerMessage(user.name())

        return answer_message.generate(for_user, {
            "details": answer
        })

    
    def generate_feedback_message(self, feedback, for_user):  
        user = UserPrompt(for_user, '')
        feedback_message = FeedbackMessage(user.name())

        return feedback_message.generate(for_user, {
            "details": feedback
        })            
    
    def message(self, input_message):     
        parsed_message = MessageParser.parse(input_message)

        action = parsed_message.get("ACTION")
        from_user = parsed_message.get("FROM")
        to_user = parsed_message.get("TO")

        if action == "step-started":
            self.handle_progress(parsed_message)
            return AcknowledgeMessage(to_user).generate(from_user, {})
        elif action == "step-completed":
            self.handle_progress(parsed_message)
            return AcknowledgeMessage(to_user).generate(from_user, {})
        elif action == "inform":
            return AcknowledgeMessage(to_user).generate(from_user, {})
        elif action == "solution-complete":
            print("In the Solution complete case")
            self.handle_progress(parsed_message)
            return AcknowledgeMessage(to_user).generate(from_user, {})

    def handle_progress(self, parsed_message):
        steps = get_steps()

        details = parsed_message.get("DETAILS")
        action = parsed_message.get("ACTION")

        if action == "step-started":
            step_numbers = self.extract_step_numbers(details)
            if not step_numbers:
                return  
            
            self.cleanup_log_file()
            min_step_number = max(map(int, step_numbers)) 
            for step_number in range(1, len(steps) + 1):
                if step_number < min_step_number:
                    pLogger.info(f"[✓] Step {step_number}: {steps[step_number - 1]}")
                elif step_number in map(int, step_numbers): 
                    pLogger.info(f"[*] Step {step_number}: {steps[step_number - 1]}")
                else:
                    pLogger.info(f"[ ] Step {step_number}: {steps[step_number - 1]}")
        elif action == "step-completed":
            step_numbers = self.extract_step_numbers(details)
            if not step_numbers:
                return  
            
            self.cleanup_log_file()
            min_step_number = max(map(int, step_numbers)) 
            for step_number in range(1, len(steps) + 1):
                if step_number < min_step_number or step_number in map(int, step_numbers): 
                    pLogger.info(f"[✓] Step {step_number}: {steps[step_number - 1]}")
                else:
                    pLogger.info(f"[ ] Step {step_number}: {steps[step_number - 1]}")
        elif action == "solution-complete":
            self.cleanup_log_file()
            print(f"Steps left: {len(steps)}")
            for step_number in range(1, len(steps) + 1):
                pLogger.info(f"[✓] Step {step_number}: {steps[step_number - 1]}")
        else:
            raise ValueError(
                f"Unknown action: {action}")

    def cleanup_log_file(self):
        self.empty_log_file(pLogger.filepath)

        pLogger.initialize_logs("Planner: planner is tasked with orchestrating the overall strategy for solving user queries. Assesses the problem statement and determines the most effective sequence of actions, delegating tasks to other agents and tools as necessary. This agent ensures that Sirji's workflow is efficient and goal-oriented.\n\n\n")

    def extract_step_numbers(self, details):
        # Define a regular expression pattern to match numbers
        pattern = r'\d+'
        
        # Use findall to extract all numbers from the details string
        numbers = re.findall(pattern, details)
        
        return numbers

    def empty_log_file(self,log_file_path):
        try:
            with open(log_file_path, "w") as log_file:
                log_file.truncate(0)
        except Exception as e:
            print(f"Failed to empty the log file: {log_file_path}. Error: {e}")