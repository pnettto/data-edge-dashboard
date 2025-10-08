import pandas as pd
def csv_to_df(f): return pd.read_csv(__file__.replace('config.py', f'{f}.csv'))


config = [
    {
        'tab': 'Resource Planning and growth',
        'items': [
             {
                'type': 'line',
                'title': 'Workload vs. Capacity Over Time',
                'description': 'Comparison of potential capacity, defined work, and recorded work hours.',
                'df': csv_to_df('df_capacity_metrics'),
                'x_field': 'month',
                'x_label': 'Month',
                'category_field': 'metric_type',
                'category_label': 'Metric',
                'category_area_highlight': ['recorded_logged_hours', 'defined_role_hours'],
                'y_field': 'hours',
                'y_label': 'Total Hours per Month',
                
            },
            

            {
                'type': 'markdown',
                'title': 'Interpreting Workload vs. Capacity',
                'content': """
                **How is the company's resource planning?**

                Since time is allocated from different perspectives that are not always aligned (e.g., project-based vs. role-based), this chart provides a high-level view of the company's workload versus its capacity over time.

                **Chart Interpretation:**
                - The **green line** represents the total hours planned based on defined roles.
                - The **purple line** shows the actual hours logged by employees.
                - The shaded area highlights the delta: **red** indicates a surplus of planned hours over logged hours, while **green** indicates more time was logged than planned.

                **Key Observation:**
                The prevalence of red areas suggests that more hours are generally planned for roles than are ultimately logged. This could indicate consistent high demand, potentially justifying the company's growth. The assumption is that a role takes 8 hours per day, which may not always reflect reality, especially if employees work overtime or if there are unplanned tasks.
                """
            },
            {
                'columns': [
                     {
                        'type': 'line',
                        'title': 'Billable vs Non-Billable Work',
                        'description': 'Comparison of billable and non-billable work hours over time',
                        'df': csv_to_df('df_billable_metrics'),
                        'x_field': 'month',
                        'x_label': 'Month',
                        'category_field': 'metric_type',
                        'category_label': 'Metric',
                        'category_area_highlight': ['billable_hours', 'non_billable_work_hours'],
                        'y_field': 'hours',
                        'y_label': 'Total Hours per Month',
                    },
                     {
                        'type': 'markdown',
                        'title': 'Billable vs Non-Billable Work',
                        'content': """
                        **How is the distribution of work hours?**

                        This chart breaks down the total logged hours into billable and non-billable categories. The shaded area highlights the delta: **red** indicates more non-billable hours than billable, while **green** indicates more billable hours.

                        **Key Observation:**
                        As we move closer to the present, there are more red areas (first non summer months in 2024), indicating a higher number of non-billable tasks, that can be related to the growth of the company (admin work, planning, etc). 
                        This is a common trend in growing companies, where the need for internal coordination and administrative tasks might require hiring specialized personnel.
                        """
                    },
                ]
            },
                
             {
                'columns': [
                     {
                        'type': 'line',
                        'title': 'Utilization over time',
                        'description': 'Utilization percentage over time',
                        'df': csv_to_df('overall_logged_utilization_timeline'),
                        'x_field': 'month',
                        'x_label': 'Month',
                        'y_field': 'logged_based_utilization',
                        'y_label': 'Utilization',
                        'trendline': True,
                        'reference_line': ('y', 80, 'Target Utilization')
                     },
                     {
                        'type': 'markdown',
                        'title': 'Interpreting Utilization',
                        'content': """
                        **How is the company's utilization trending?**

                        Utilization measures the percentage of billable hours against total logged hours. This chart tracks that metric over time.

                        **Key Observation:**
                        There is a slight downward trend in utilization, which can be seen as a side effect of the company's growth. As the team expands, more time is inevitably spent on non-billable but necessary activities like administration, internal coordination, and business development. 
                        
                        Currently, the company does not have dedicated administrative staff or interns to handle these tasks. To reverse this trend and aim for a target like 80% utilization, the company may need to consider structural changes or process optimizations.
                        """
                     },
                ]
            },

            {
                'type': 'markdown',
                'title': 'Effort and Workload Analysis',
                'content': """
                **As we grow, how do we manage our workload? Can we sustain our growth?**

                We calculated two metrics: Work in Progress (WIP) and Effort per Project. WIP indicates the number of active projects per month, while Effort per Project measures the logged hours per quarter divided by the number of projects finished in that quarter.

                **Chart Interpretation:**
                - The WIP chart shows a steady grow in the number of active projects, indicating a healthy pipeline and sustained growth.
                - The Effort per Project chart reveals a decreasing trend, suggesting that as the company grows, it is becoming more efficient in managing projects.

                **Key Observation:**
                The analysis of both charts indicates a healthy pipeline: more projects are being worked on over time, while the effort required per project is decreasing. This suggests that the company is improving its efficiency and can sustain its growth trajectory.
                """
            },
             {
                'columns': [
                     {
                        'type': 'line',
                        'title': 'Effort per Project',
                        'description': 'Average effort per project (hours spent vs headcount) over time',
                        'df': csv_to_df('headcount_vs_effort'),
                        'x_field': 'quarter_x',
                        'x_label': 'Quarter',
                        'y_field': 'avg_effort_per_project',
                        'y_label': 'Avg Effort per Project',
                        'trendline': True
                    },
                     {
                        'type': 'line',
                        'title': 'Evolution of Work In Progress',
                        'description': 'Amount of active projects each month',
                        'df': csv_to_df('monthly_wip_load'),
                        'x_field': 'month',
                        'x_label': 'Month',
                        'y_field': 'wip_project_count',
                        'y_label': 'Project Count',
                        'trendline': True
                    },
                ]
            },

            {
                'type': 'markdown',
                'title': 'Diving into resource allocation',
                'content': """
                **What can we change to improve in the way we allocate our time?**
                We have, so far, reviewd the overall utilization and workload of the company. One of its objectives is to reduce the dependence on broker deals, and create more direct relationshipts.
                Most of the weight of that work falls under the senior profiles, which would need to re-allocate their efforts efficiently, with the help of the rest of the company.
                We modeled how the utilization of the company is distributed by seniority, and how it has evolved over time. We see that, even though it seems to be well distributed, in order for the senior roles to have more time, they would need to reduce their utilization time. 
                In the last months the utilization in general (and thus) the seniors, has increased, as it has happened in other periods. Project-wise this is good but in order to grow, their allocation of time needs to change.
                
                Strategic Levers for Creating Capacity

                1. Create Capacity (Short-Term Tactics)
                The most immediate path to freeing up senior time is through aggressive delegation and automation of lower-value tasks.

                - Delegate Non-Billable & Administrative Work: A significant portion of time is spent on non-billable activities. Hiring junior or administrative staff would allow seniors to offload these responsibilities. While some roles are not interchangeable, many administrative and coordination tasks can be effectively delegated.

                - Leverage AI for Automation: Given the company's proficiency with AI tools, deploying an AI agent for administrative tasks like scheduling, data compilation, and initial report drafting could create immediate and significant time savings with minimal overhead.

                2. Restructure the Workload (Long-Term Strategy)
                A sustainable solution requires structurally shifting the responsibility for business development and complex project work.

                - Introduce a Dedicated Sales Role: The most direct way to protect senior time is to hire a dedicated sales or business development professional. While this represents a new cost center, it professionalizes the sales function and guarantees that a portion of the company's resources is always focused on building a direct pipeline.

                - Empower Mid-Level Staff: Create a formal mentorship track where seniors actively train mid-level staff to handle more complex project management and client-facing responsibilities. This creates a clear path for growth and enables seniors to progressively transition their focus from "doing the work" to "guiding the work."

                **Actionables:**
                
                
                Immediate Action (Next 30 Days):
                - Quantify the Load: Conduct a detailed audit of the non-billable tasks currently handled by senior staff to identify the top 5-10 activities that are prime candidates for delegation or automation.

                Short-Term Plan (Next 3-6 Months):
                - Hire an Administrative Assistant: Prioritize the addition of a junior or administrative role to absorb the tasks identified in the audit.
                - Pilot an AI Agent: Begin a trial of an AI-powered administrative assistant to measure its impact on senior productivity.

                Long-Term Strategy (Next 6-12 Months):
                - Develop the Business Case for a Sales Hire: Model the financial impact of a dedicated sales role. Project the break-even point based on the value of freed-up senior time and the expected increase in direct deal flow. This will provide a data-driven foundation for the hiring decision.
                """
            },
             {
                'columns': [
                      {
                        'type': 'bar',
                        'title': 'Utilization by Seniority',
                        'description': 'AVG Utilization by Seniority',
                        'df': csv_to_df('utilization_by_seniority'),
                        'x_field': 'seniority',
                        'x_label': 'Seniority',            
                        'y_field': 'logged_based_utilization',
                        'y_label': 'Utilization',
                        'reference_line': ('y', 80, 'Target Utilization'),
                        # 'forecast': True
                     },
                      {
                        'type': 'line',
                        'title': 'Utilization by Seniority',
                        'description': 'Logged Utilization over time by seniority',
                        'df': csv_to_df('monthly_logged_utilization'),
                        'x_field': 'month',
                        'x_label': 'Month',
                        'y_field': 'logged_based_utilization',
                        'y_label': 'Utilization',
                        'category_field': 'seniority',
                        'category_label': 'Seniority'
                     },
                ]
            },
            
           
           
           
            
                
            

            

        ]
    },
]
