from locust import HttpUser, TaskSet, task, between
from locust.exception import StopUser
import time
import random

class AllLimericksSection(TaskSet):
    @task
    def all_tasks(self):
        self.client.get("")
        self.client.get("limericks/")
        for id in range(5):
            self.client.get(f"limericks/{id + 1}", name="/limericks/{id}")
            time.sleep(5)
        self.client.get("generate/")
        csrf_token = self.client.cookies['csrftoken']
        adjectives_profession = {"severe":["woman","girl","judge","actor","barber"], 
            "embarrassed":["coach","man","boy","chef","child"],
            "pretty":["butcher","dentist","plumber","pilot","teacher"],
            "prudent":["doctor","surgeon","waitress","cashier","artist"],
            "keen":["banker","builder","painter","architect","jeweler"]}

        adjective_single = random.choice(list(adjectives_profession.keys()))
        profession_single = random.choice(adjectives_profession[adjective_single])
        print(f'Adjective single is {adjective_single} and prof single {profession_single}')
        generate_query_single = {'csrfmiddlewaretoken': [csrf_token], 'adjective': [adjective_single], 'profession': [profession_single], 'kind': ['single']}
        header_query = {'X-CSRFToken': csrf_token}
        self.client.post("generate/", data=generate_query_single, headers=header_query, name="single-generation")
        adjective_multi = random.choice(list(adjectives_profession.keys()))
        profession_multi = random.choice(adjectives_profession[adjective_multi])
        print(f'Adjective multi is {adjective_multi} and prof multi {profession_multi}')
        generate_query_mult = {'csrfmiddlewaretoken': [csrf_token], 'adjective': [adjective_multi], 'profession': [profession_multi], 'kind': ['multiple']}
        self.client.post("generate/", data=generate_query_mult, headers=header_query, name="multi-generation")
        raise StopUser()


class ListPostUser(HttpUser):
    wait_time = between(5, 10)
    tasks = [AllLimericksSection]