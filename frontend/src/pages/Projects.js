// src/Pages/Projects.js
import React, { useState, useEffect } from 'react';
import { getProjects, createProject } from '../services/apiService';

const Projects = () => {
  const [projects, setProjects] = useState([]);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDescription, setNewProjectDescription] = useState('');

  useEffect(() => {
    // Fetch projects when the component mounts
    const fetchProjects = async () => {
      try {
        const data = await getProjects();
        setProjects(data);
      } catch (error) {
        console.error('Error fetching projects:', error);
      }
    };

    fetchProjects();
  }, []);

  const handleCreateProject = async () => {
    try {
      const newProject = {
        name: newProjectName,
        description: newProjectDescription,
      };
      await createProject(newProject);
      // Re-fetch the projects after creation
      const data = await getProjects();
      setProjects(data);
    } catch (error) {
      console.error('Error creating project:', error);
    }
  };

  return (
    <div>
      <h1>Projects</h1>
      <ul>
        {projects.map((project) => (
          <li key={project.id}>
            {project.name}: {project.description}
          </li>
        ))}
      </ul>

      <h2>Create New Project</h2>
      <input
        type="text"
        value={newProjectName}
        onChange={(e) => setNewProjectName(e.target.value)}
        placeholder="Project Name"
      />
      <input
        type="text"
        value={newProjectDescription}
        onChange={(e) => setNewProjectDescription(e.target.value)}
        placeholder="Project Description"
      />
      <button onClick={handleCreateProject}>Create Project</button>
    </div>
  );
};

export default Projects;
