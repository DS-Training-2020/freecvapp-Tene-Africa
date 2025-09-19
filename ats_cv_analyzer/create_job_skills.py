import os

# Ensure the job_keywords folder exists
folder = "job_keywords"
os.makedirs(folder, exist_ok=True)

# Dictionary of job roles and their keywords
keywords_dict = {
    "software_engineer.txt": """Python, Java, C++, JavaScript, SQL, Git, Docker, Kubernetes, REST API, Agile, Cloud, AWS, Azure, Google Cloud, Linux, HTML, CSS, React, Node.js, CI/CD, DevOps, Microservices, System Design, Testing, Debugging, API Integration, Problem Solving""",

    "data_scientist.txt": """Python, R, SQL, Machine Learning, Deep Learning, Statistics, Data Analysis, Data Visualization, Pandas, NumPy, TensorFlow, PyTorch, Scikit-learn, Natural Language Processing, Big Data, Hadoop, Spark, Data Mining, Cloud, AWS, Azure, Google Cloud, ETL, Tableau, Power BI, Data Cleaning, Predictive Modeling, Jupyter""",

    "data_engineer.txt": """Python, SQL, ETL, Data Pipelines, Big Data, Hadoop, Spark, Kafka, Airflow, Cloud, AWS, Azure, Google Cloud, Snowflake, Redshift, Databricks, Data Warehousing, Data Lakes, SQL Optimization, NoSQL, MongoDB, Cassandra, Scala, Java, Docker, Kubernetes""",

    "devops_engineer.txt": """CI/CD, Git, Jenkins, Docker, Kubernetes, Terraform, Ansible, AWS, Azure, Google Cloud, Linux, Bash, Python, Monitoring, Prometheus, Grafana, CloudFormation, Security, Networking, Scripting, Automation, Infrastructure as Code, Configuration Management""",

    "cybersecurity_analyst.txt": """Cybersecurity, Risk Assessment, Incident Response, SIEM, Firewall, IDS, IPS, Threat Hunting, Vulnerability Assessment, Penetration Testing, Ethical Hacking, Encryption, Network Security, Endpoint Security, Cloud Security, Compliance, NIST, ISO 27001, SOC, Security Policies""",

    "business_analyst.txt": """Business Analysis, Requirements Gathering, Stakeholder Management, Process Improvement, Data Analysis, SQL, Excel, UML, Use Cases, Agile, Scrum, Communication, Documentation, Gap Analysis, Reporting, Problem Solving, Decision Making""",

    "mechanical_engineer.txt": """Mechanical Design, CAD, SolidWorks, AutoCAD, Thermodynamics, Manufacturing, Materials, Fluid Mechanics, HVAC, Robotics, Prototyping, 3D Printing, Simulation, Stress Analysis, Quality Control, Product Development""",

    "civil_engineer.txt": """Civil Engineering, Structural Engineering, AutoCAD, Construction, Project Management, Surveying, Concrete, Steel, Geotechnical, Transportation Engineering, Environmental Engineering, Hydraulics, Building Codes, Cost Estimation, Site Inspection""",

    "electrical_engineer.txt": """Circuit Design, Electronics, Power Systems, MATLAB, Embedded Systems, PCB Design, Microcontrollers, Control Systems, Signal Processing, Renewable Energy, Automation, Testing, Troubleshooting, Robotics, IoT""",

    "uiux_designer.txt": """UI Design, UX Design, Wireframing, Prototyping, Figma, Sketch, Adobe XD, Usability Testing, User Research, Interaction Design, Visual Design, Accessibility, Mobile Design, Responsive Design, Information Architecture, Creativity""",

    "project_manager.txt": """Project Management, Agile, Scrum, Kanban, Jira, Trello, Leadership, Communication, Stakeholder Management, Risk Management, Budgeting, Scheduling, Planning, Resource Allocation, Change Management, Team Management, PMP, Prince2, MS Project""",

    "product_manager.txt": """Product Management, Roadmap, Strategy, Agile, Scrum, Market Research, Wireframing, Prototyping, User Stories, Prioritization, Stakeholder Management, Analytics, Go-to-Market, A/B Testing, Communication, Leadership""",

    "operations_manager.txt": """Operations Management, Supply Chain, Logistics, Process Improvement, Lean, Six Sigma, Inventory Management, Quality Control, Scheduling, Forecasting, Vendor Management, Procurement, Cost Reduction, Efficiency, ERP Systems""",

    "supply_chain.txt": """Supply Chain, Logistics, Procurement, Inventory Management, Distribution, Warehouse Management, Demand Planning, Transportation, ERP, SAP, Forecasting, Vendor Management, Sourcing, Shipping, Import/Export""",

    "consultant.txt": """Consulting, Strategy, Business Analysis, Market Research, Financial Analysis, Problem Solving, Client Management, Stakeholder Engagement, Presentation Skills, PowerPoint, Excel, Data Analysis, Change Management""",

    "graphic_designer.txt": """Adobe Photoshop, Adobe Illustrator, Adobe InDesign, Figma, Sketch, Canva, UI Design, UX Design, Typography, Branding, Logo Design, Color Theory, Layout, Wireframing, Prototyping, Visual Design, Adobe XD, Motion Graphics""",

    "marketing_specialist.txt": """Marketing Strategy, Digital Marketing, SEO, SEM, Content Marketing, Social Media, Google Analytics, Email Marketing, PPC, Advertising, Branding, Campaign Management, Copywriting, Public Relations, Market Research, CRM, HubSpot, Salesforce, Conversion Optimization""",

    "content_writer.txt": """Content Writing, Copywriting, Blogging, SEO, Storytelling, Editing, Proofreading, Research, Social Media, Marketing, Creativity, Grammar, WordPress, Journalism, Press Releases, Creative Writing""",

    "nurse.txt": """Nursing, Patient Care, Clinical Skills, Medical Records, Medication Administration, Vital Signs, IV Therapy, Emergency Care, Communication, Compassion, Critical Thinking, Health Education, Infection Control, Pediatrics, Geriatrics, Surgery, Documentation""",

    "pharmacist.txt": """Pharmacy, Prescriptions, Medication, Pharmacology, Drug Interactions, Patient Counseling, Clinical Knowledge, Dosage, Compounding, Inventory, Regulatory Compliance, Research, Healthcare, Pharmacovigilance""",

    "healthcare_administrator.txt": """Healthcare Management, Hospital Operations, Compliance, Patient Care, Medical Records, Budgeting, Staffing, Scheduling, Healthcare Policy, Risk Management, Insurance, Communication, Strategic Planning""",

    "teacher.txt": """Teaching, Lesson Planning, Classroom Management, Curriculum Development, Student Assessment, Educational Technology, Communication, Collaboration, Child Development, Special Education, Differentiated Instruction, Student Engagement, Mentoring, Tutoring, Parent Communication""",

    "human_resources.txt": """Recruitment, Talent Acquisition, HR Policies, Payroll, Employee Relations, Onboarding, Training, Performance Management, Compensation, Benefits, HRIS, Compliance, Diversity, Workplace Safety, Conflict Resolution, Employee Engagement, Labor Laws""",

    "sales_representative.txt": """Sales, Customer Relationship, Negotiation, Cold Calling, Prospecting, Lead Generation, CRM, Salesforce, Pipeline Management, Closing Deals, Presentation Skills, Account Management, Business Development, Upselling, Target Achievement, Client Retention""",

    "financial_analyst.txt": """Financial Analysis, Accounting, Excel, Budgeting, Forecasting, Financial Modeling, Valuation, Investment, Reporting, Financial Statements, Risk Management, Auditing, Corporate Finance, Strategy, Data Analysis""",

    # ✅ New universal soft skills file
    "general_keywords.txt": """Communication, Teamwork, Leadership, Problem Solving, Time Management, Adaptability, Creativity, Collaboration, Critical Thinking, Decision Making, Organization, Interpersonal Skills, Negotiation, Emotional Intelligence, Active Listening, Presentation Skills, Conflict Resolution, Professionalism, Work Ethic, Multitasking"""
}

# Create each file
for filename, content in keywords_dict.items():
    filepath = os.path.join(folder, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ Created {filepath}")

print("\nAll 26 job keyword files created successfully! (25 roles + general soft skills)")
