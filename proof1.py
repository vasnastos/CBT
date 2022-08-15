from ortools.sat.python import cp_model

class sol_callback(cp_model.CpSolverSolutionCallback):
    def __init__(self,dvar_set):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.dvars=dvar_set
        self.sid=1
    
    def on_solution_callback(self):
        print(f'Solution id:{self.sid}')
        self.sid+=1
        for x in self.dvars:
            print(f'{x.Name()}=>{self.Value(x)}')
        print()
        

model=cp_model.CpModel()
X1=model.NewBoolVar(name='X1')
X2=model.NewBoolVar(name='X2')


X3=model.NewBoolVar(name='X3')
X4=model.NewBoolVar(name='X4')

model.Add(X1+X2+X3>=2)
model.Add(X4==1).OnlyEnforceIf(X3)

model.Minimize(sum([X4]))

solver=cp_model.CpSolver()
# status=solver.SearchForAllSolutions(model,sol_callback([X1,X2,X3]))
status=solver.Solve(model,cp_model.ObjectiveSolutionPrinter())
if status==cp_model.OPTIMAL:
    print(solver.Value(X1))
    print(solver.Value(X2))
