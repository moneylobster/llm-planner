from llmcall import llmcall
import languagemodels as lm

from vizclass import visualize

lm.set_max_ram(4)

SIMLOGFLAG=True

def simlog(txt):
    global SIMLOGFLAG
    if SIMLOGFLAG:
        print(txt)

class Agent():
    def __init__(self, house):
        self.house=house

        simlog("PREP: Generating action list...")
        self.allactions=self.getallactions()
        self.hand=""
        self.location=self.house.rooms[0]

    @property
    def items(self):
        return self.location.items

    @property
    def rooms(self):
        return [r.name for r in self.house.rooms]

    @property
    def actions(self):
        acts=[]
        acts+=[f"pick up {item}" for item in self.items]
        acts+=[f"move to {room}" for room in self.rooms]
        acts+=["put down the item being held"]
        acts+=["done"]
        return acts

    def getallactions(self):
        global SIMLOGFLAG
        oldsimlogflag=SIMLOGFLAG
        SIMLOGFLAG=False # turn simlog off to prevent unnecessary prints
        
        res={}
        for room in self.rooms:
            self.move(room)
            res[room]=self.actions
            
        SIMLOGFLAG=oldsimlogflag
        return res
        
    def pick(self, item):
        '''
        try to pick up an item
        '''
        if self.hand=="" and self.location.pick(item):
            self.hand=item
            simlog(f"PICK: Picked up item: {item}")
        else:
            simlog(f"ERR: Cannot pick up item: {item}")
            
    def place(self):
        '''
        place the item in hand
        '''
        if self.hand!="":
            simlog(f"PLACE: Placed item: {self.hand}")
            self.location.place(self.hand)
            self.hand=""
        else:
            simlog("ERR: Tried to place with nothing in hand")

    def move(self, room):
        for i,val in enumerate(self.house.rooms):
            if val.name==room:
                break
        self.location=self.house.rooms[i]
        simlog(f"MOVE: Moved to room: {self.location.name}")

class Planner(Agent):
    def __init__(self, house, goal):
        self.goal=goal
        super().__init__(house)

class ZeroShotPlanner(Planner):
    """
    This planner implements Huang's zero-shot planning algo:
    The LLM makes the plan step by step, each step is replaced
    by the closest realizable action there is to it via text
    embeddings before prompting LLM for the next step.
    """
    def __init__(self, house, goal):
        super().__init__(house, goal)

        self.actprompt="His actions for this goal are:\n"
        
        self.step=1
        self.done=False
        self.actlist=[]
        self.resplist=[]

        simlog("PREP: Generating embeddings for all actions...")
        self.actionembeddings=self.generate_embeddings()

    def construct_prompt(self):
        
        initprompt=f"""
        Rob is a robot that can pick up and place things.
        He makes plans to fulfill goals given by the user.
        Done means the goal has been completed.
        Keep in mind that there are other items in the other rooms.
        An example for the goal "Pick up the stool":
        1. pick up stool
        2. done
        
        He is in a house with multiple rooms: {self.rooms}
        His current goal is: {self.goal}
        Item in Rob's hand: {self.hand}
        The possible actions he can take are: {self.actions}
        """
        
        return (
            initprompt+
            self.actprompt
        )
        
    def start(self):
        '''
        start the planning & execution process
        '''
        simlog(f"START: Starting goal: {self.goal}")
        while not self.done:
            self.iterate()
        print("---------")
        print(f"RESPS:\n{self.resplist}\nACTIONS:\n{self.actlist}")
        
    def iterate(self):
        '''
        go through one iteration of the planning loop.
        '''
        # construct prompt
        self.actprompt+=f"\n{self.step}. "
        # Call LLM
        resp=lm.do(self.construct_prompt())
        # resp=llmcall(self.construct_prompt())

        simlog(f"LLM: Response was: {resp}")
        self.resplist.append(resp) # log resp

        suggested_step=self.extract_step_from_resp(resp)
        self.apply_step(suggested_step)

        self.step+=1 #increment step count

        visualize(self)

    def extract_step_from_resp(self, resp):
        # if the response contains a step number
        currstep=resp.find(f"{self.step}. ") #does the current step exist?
        nextstep=resp.find(f"{self.step+1}. ") #does the next step exist?
        if currstep>=0:
            if nextstep>=0:
                return resp[currstep:nextstep]
            else:
                return resp[currstep:]
        return resp
            
        
    def apply_step(self, suggested_step):
        # get the closest action to the suggested step
        closest_action=self.actionembeddings[self.location.name].get_match(suggested_step)
        self.actlist.append(closest_action) # log action
        # execute action
        if closest_action.startswith("pick"):
            self.pick(closest_action[8:])
        elif closest_action.startswith("put"):
            self.place()
        elif closest_action.startswith("move"):
            self.move(closest_action[8:])
        elif closest_action.startswith("done"):
            self.done=True
        else:
            simlog(f"ERR: Unrealizable action: {closest_action}")
        # replace action (with results?) in prompt
        # TODO add results
        self.actprompt+=closest_action

    def generate_embeddings(self):
        '''
        generate embeddings for actions
        '''
        emb={}
        for room, acts in self.allactions.items():
            rc=lm.RetrievalContext()
            for act in acts:
                rc.store(act)
            emb[room]=rc
        return emb
