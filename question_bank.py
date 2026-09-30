# =========================================================
# GUARDIANAI - ADAPTIVE QUESTION BANK
# =========================================================

QUESTION_BANK = {

    # =====================================================
    # SQL
    # =====================================================

    "SQL": {

        "Beginner": [
            {
                "question": "Which SQL command is used to retrieve data from a table?",
                "options": [
                    "GET",
                    "SELECT",
                    "FETCH",
                    "READ"
                ],
                "answer": "SELECT"
            },
            {
                "question": "Which SQL command is used to add a new row?",
                "options": [
                    "INSERT",
                    "ADD",
                    "CREATE",
                    "UPDATE"
                ],
                "answer": "INSERT"
            }
        ],

        "Intermediate": [
            {
                "question": "Which SQL clause is used to filter grouped results?",
                "options": [
                    "WHERE",
                    "GROUP BY",
                    "HAVING",
                    "ORDER BY"
                ],
                "answer": "HAVING"
            },
            {
                "question": "Which JOIN returns matching records from both tables?",
                "options": [
                    "LEFT JOIN",
                    "RIGHT JOIN",
                    "INNER JOIN",
                    "FULL JOIN"
                ],
                "answer": "INNER JOIN"
            }
        ],

        "Advanced": [
            {
                "question": "Which SQL technique is commonly used to rank rows within partitions?",
                "options": [
                    "GROUP BY",
                    "Window Functions",
                    "UNION",
                    "DELETE"
                ],
                "answer": "Window Functions"
            }
        ]
    },


    # =====================================================
    # NORMALIZATION
    # =====================================================

    "Normalization": {

        "Beginner": [
            {
                "question": "What is the main purpose of database normalization?",
                "options": [
                    "Increase redundancy",
                    "Reduce redundancy",
                    "Delete tables",
                    "Increase storage"
                ],
                "answer": "Reduce redundancy"
            }
        ],

        "Intermediate": [
            {
                "question": "Which normal form removes partial dependency?",
                "options": [
                    "1NF",
                    "2NF",
                    "3NF",
                    "BCNF"
                ],
                "answer": "2NF"
            }
        ],

        "Advanced": [
            {
                "question": "Which normal form is stricter than 3NF?",
                "options": [
                    "1NF",
                    "2NF",
                    "BCNF",
                    "4NF"
                ],
                "answer": "BCNF"
            }
        ]
    },


    # =====================================================
    # TRANSACTIONS
    # =====================================================

    "Transactions": {

        "Beginner": [
            {
                "question": "Which property ensures a transaction is completed fully or not at all?",
                "options": [
                    "Consistency",
                    "Atomicity",
                    "Isolation",
                    "Durability"
                ],
                "answer": "Atomicity"
            }
        ],

        "Intermediate": [
            {
                "question": "Which ACID property ensures committed data is not lost?",
                "options": [
                    "Atomicity",
                    "Consistency",
                    "Isolation",
                    "Durability"
                ],
                "answer": "Durability"
            }
        ],

        "Advanced": [
            {
                "question": "Which mechanism is commonly used to control concurrent transactions?",
                "options": [
                    "Concurrency Control",
                    "Normalization",
                    "Indexing",
                    "Projection"
                ],
                "answer": "Concurrency Control"
            }
        ]
    },


    # =====================================================
    # INDEXING
    # =====================================================

    "Indexing": {

        "Beginner": [
            {
                "question": "What is the main purpose of an index in a database?",
                "options": [
                    "Speed up data retrieval",
                    "Delete data",
                    "Increase redundancy",
                    "Create users"
                ],
                "answer": "Speed up data retrieval"
            }
        ],

        "Intermediate": [
            {
                "question": "Which data structure is commonly used to implement database indexes?",
                "options": [
                    "Stack",
                    "Queue",
                    "B-tree",
                    "Linked List"
                ],
                "answer": "B-tree"
            }
        ],

        "Advanced": [
            {
                "question": "What is a potential disadvantage of having too many indexes?",
                "options": [
                    "Faster INSERT operations",
                    "More storage and slower writes",
                    "No effect",
                    "Automatic normalization"
                ],
                "answer": "More storage and slower writes"
            }
        ]
    },


    # =====================================================
    # INHERITANCE
    # =====================================================

    "inheritance": {

        "Beginner": [
            {
                "question": "What is inheritance in Object-Oriented Programming?",
                "options": [
                    "A child class acquiring properties and methods from a parent class",
                    "Deleting a parent class",
                    "Creating a database table",
                    "Hiding all methods"
                ],
                "answer": "A child class acquiring properties and methods from a parent class"
            },
            {
                "question": "What is the class that provides properties and methods to another class called?",
                "options": [
                    "Child class",
                    "Parent class",
                    "Object class",
                    "Method class"
                ],
                "answer": "Parent class"
            },
            {
                "question": "What is one major benefit of inheritance?",
                "options": [
                    "Code reusability",
                    "Data deletion",
                    "Database normalization",
                    "Slower execution"
                ],
                "answer": "Code reusability"
            }
        ],

        "Intermediate": [
            {
                "question": "What is another name for a parent class?",
                "options": [
                    "Superclass",
                    "Subclass",
                    "Instance",
                    "Object"
                ],
                "answer": "Superclass"
            },
            {
                "question": "What is another name for a child class?",
                "options": [
                    "Superclass",
                    "Subclass",
                    "Parent",
                    "Package"
                ],
                "answer": "Subclass"
            },
            {
                "question": "Which relationship is represented by inheritance?",
                "options": [
                    "IS-A relationship",
                    "HAS-A relationship",
                    "USES-A relationship",
                    "PART-OF relationship"
                ],
                "answer": "IS-A relationship"
            }
        ],

        "Advanced": [
            {
                "question": "Which type of inheritance allows a class to inherit from more than one parent class?",
                "options": [
                    "Single inheritance",
                    "Multiple inheritance",
                    "Multilevel inheritance",
                    "Hierarchical inheritance"
                ],
                "answer": "Multiple inheritance"
            },
            {
                "question": "A class inherits from a class that itself inherits from another class. What is this called?",
                "options": [
                    "Multiple inheritance",
                    "Multilevel inheritance",
                    "Single inheritance",
                    "Hybrid inheritance"
                ],
                "answer": "Multilevel inheritance"
            }
        ]
    },


    # =====================================================
    # POLYMORPHISM
    # =====================================================

    "polymorphism": {

        "Beginner": [
            {
                "question": "What does polymorphism mean?",
                "options": [
                    "One interface or method having different forms",
                    "Creating only one object",
                    "Deleting methods",
                    "Hiding data permanently"
                ],
                "answer": "One interface or method having different forms"
            },
            {
                "question": "Which OOP concept allows the same method name to behave differently?",
                "options": [
                    "Inheritance",
                    "Polymorphism",
                    "Encapsulation",
                    "Abstraction"
                ],
                "answer": "Polymorphism"
            }
        ],

        "Intermediate": [
            {
                "question": "Which concept is commonly associated with method overriding?",
                "options": [
                    "Polymorphism",
                    "Normalization",
                    "Indexing",
                    "Compilation"
                ],
                "answer": "Polymorphism"
            }
        ],

        "Advanced": [
            {
                "question": "Which type of polymorphism is commonly achieved using method overriding?",
                "options": [
                    "Runtime polymorphism",
                    "Static storage",
                    "Database polymorphism",
                    "File polymorphism"
                ],
                "answer": "Runtime polymorphism"
            }
        ]
    },


    # =====================================================
    # ENCAPSULATION
    # =====================================================

    "encapsulation": {

        "Beginner": [
            {
                "question": "What is encapsulation?",
                "options": [
                    "Wrapping data and methods together in a class",
                    "Deleting data",
                    "Creating multiple databases",
                    "Inheriting every class"
                ],
                "answer": "Wrapping data and methods together in a class"
            }
        ],

        "Intermediate": [
            {
                "question": "Which access modifier is commonly used to restrict direct access to data in Java?",
                "options": [
                    "private",
                    "public",
                    "static",
                    "final"
                ],
                "answer": "private"
            }
        ],

        "Advanced": [
            {
                "question": "Encapsulation mainly helps protect an object's internal state from what?",
                "options": [
                    "Uncontrolled direct access",
                    "Compilation",
                    "Inheritance",
                    "Object creation"
                ],
                "answer": "Uncontrolled direct access"
            }
        ]
    },


    # =====================================================
    # ABSTRACTION
    # =====================================================

    "abstraction": {

        "Beginner": [
            {
                "question": "What is abstraction in Object-Oriented Programming?",
                "options": [
                    "Showing essential details while hiding implementation details",
                    "Showing every implementation detail",
                    "Deleting all methods",
                    "Creating database indexes"
                ],
                "answer": "Showing essential details while hiding implementation details"
            }
        ],

        "Intermediate": [
            {
                "question": "Which Java feature can be used to achieve abstraction?",
                "options": [
                    "Abstract class",
                    "Database",
                    "Array",
                    "Package only"
                ],
                "answer": "Abstract class"
            }
        ],

        "Advanced": [
            {
                "question": "Which concept focuses on what an object does rather than how it does it?",
                "options": [
                    "Abstraction",
                    "Inheritance",
                    "Normalization",
                    "Indexing"
                ],
                "answer": "Abstraction"
            }
        ]
    }

}


# =========================================================
# GET QUESTIONS
# =========================================================

def get_questions(topic, level):

    topic_data = QUESTION_BANK.get(topic)

    if not topic_data:
        return []

    return topic_data.get(
        level,
        []
    )