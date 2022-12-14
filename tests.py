import unittest as un
from problem import Problem

class DitTest(un.TestCase):
    def test_input(self):
        problem=Problem()
        self.assertEqual(problem.number_of_lecturers(),17)
        self.assertEqual(problem.number_of_curriculas(),11)
        self.assertEqual(problem.number_of_rooms(),9)
        self.assertEqual(problem.number_of_courses(),64)
        self.assertEqual(problem.days,5)
        self.assertEqual(problem.periods_per_day,12)
    
    def testLecturer(self):
        pass
    
    def testCourses(self):
        pass


if __name__=='__main__':
    un.main()