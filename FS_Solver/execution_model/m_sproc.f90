! Description:
! Solution procedures.
module m_sproc
    use linear_algebra
    use data_model
    use m_gproc
    implicit none
    
    private
    public static_analysis
    
    contains
    
    ! Description:
    ! Performs a static analysis
    type(t_odb) function static_analysis(mdb) result(odb)
        ! procedure arguments
        type(t_mdb), intent(in) :: mdb ! model database
        
        ! additional variables
        type(t_sparse)              :: Kaa, Kab              ! global stiffness matrix
        type(t_vector)              :: Pa                    ! equivalent nodal loads vector
        type(t_vector)              :: Fe                    ! external nodal forces
        type(t_vector)              :: Ua                    ! unknown displacements
        type(t_vector)              :: Ub                    ! prescribed nodal displacements
        type(t_vector)              :: R                     ! reaction forces
        type(t_vector)              :: Fa, Fb                ! internal nodal forces
        type(t_matrix), allocatable :: strain_ips(:)         ! strain at the integration points (basic components)
        type(t_matrix), allocatable :: stress_ips(:)         ! stress at the integration points (basic components
        type(t_matrix), allocatable :: strain_nodes(:)       ! strain at the element nodes (basic components)
        type(t_matrix), allocatable :: stress_nodes(:)       ! stress at the element nodes (basic components)
        type(t_matrix), allocatable :: strain_extra_nodes(:) ! strain at the element nodes (basic components + extra measures)
        type(t_matrix), allocatable :: stress_extra_nodes(:) ! stress at the element nodes (basic components + extra measures)
        type(t_matrix)              :: strain_extra_mesh     ! strain at the mesh nodes (basic components + extra measures)
        type(t_matrix)              :: stress_extra_mesh     ! stress at the mesh nodes (basic components + extra measures)
        type(t_matrix)              :: displacement          ! displacements at the mesh nodes
        type(t_matrix)              :: reaction              ! reaction forces at the mesh nodes
        
        ! allocate storage
        allocate(strain_ips(mdb%mesh%n_elements))
        allocate(stress_ips(mdb%mesh%n_elements))
        allocate(strain_nodes(mdb%mesh%n_elements))
        allocate(stress_nodes(mdb%mesh%n_elements))
        allocate(strain_extra_nodes(mdb%mesh%n_elements))
        allocate(stress_extra_nodes(mdb%mesh%n_elements))
        
        ! compute global stiffness matrix
        call g_get_K(mdb%n_adofs, mdb%n_idofs, mdb%mesh, mdb%sections, mdb%materials, Kaa, Kab)
        
        ! compute equivalent nodal loads vector
        Pa = new_vector(mdb%n_adofs)
        call g_add_Pc(mdb%mesh%m_space, mdb%n_cloads, mdb%mesh%nodes, mdb%cloads, mdb%nsets, Pa) ! add concentrated loads
        
        ! add contribution from prescribed nodal displacements
        Ub = g_get_Ub(mdb%mesh%m_space, mdb%n_idofs, mdb%n_boundaries, mdb%mesh%nodes, mdb%boundaries, mdb%nsets)
        Fe = subtract(Pa, multiply(Kab, Ub))
        
        ! compute unknown displacements
        Ua = solve(Kaa, Fe)
        
        ! compute reaction forces
        R = multiply(Kab, Ua, transposeA=.true.)
        
        ! compute internal nodal forces
        ! also computes strains and stresses at the integration points
        call g_get_F(mdb%n_adofs, mdb%n_idofs, mdb%mesh, mdb%sections, mdb%materials, Ua, Ub, Fa, Fb, strain_ips, stress_ips)
        
        ! compute residual (infinity norm of the out-of-balance forces vector)
        print '("Infinity norm of the out-of-balance forces vector (residual): ",SP,E11.4)', maxval(abs(Fe%at(:) - Fa%at(:)))
        
        ! perform extrapolation from element integration points to element nodes
        ! deallocate unused storage
        call extrapolate(mdb%mesh%n_elements, mdb%mesh%elements, strain_ips, strain_nodes); if (allocated(strain_ips)) deallocate(strain_ips)
        call extrapolate(mdb%mesh%n_elements, mdb%mesh%elements, stress_ips, stress_nodes); if (allocated(stress_ips)) deallocate(stress_ips)
        
        ! compute additional strain and stress measures (principal strains, principal stresses, and equivalent stresses)
        ! deallocate unused storage
        call extra_strain(strain_nodes, strain_extra_nodes); if (allocated(strain_nodes)) deallocate(strain_nodes)
        call extra_stress(stress_nodes, stress_extra_nodes); if (allocated(stress_nodes)) deallocate(stress_nodes)
        
        ! compute values at mesh nodes (perform final smoothing)
        strain_extra_mesh = average(mdb%mesh, strain_extra_nodes, 10); if (allocated(strain_extra_nodes)) deallocate(strain_extra_nodes)
        stress_extra_mesh = average(mdb%mesh, stress_extra_nodes, 13); if (allocated(stress_extra_nodes)) deallocate(stress_extra_nodes)
        
        ! convert global vectors to result matrices
        displacement = convert_vector(mdb%mesh%m_space, mdb%mesh%n_nodes, mdb%mesh%nodes, Ua, Ub)
        reaction     = convert_vector(mdb%mesh%m_space, mdb%mesh%n_nodes, mdb%mesh%nodes, new_vector(mdb%n_adofs), R)
        
        ! create output database
        ! <frame_number>:<nodal_scalar_group>:<nodal_scalar_name>
        odb = new_odb(mdb%mesh%n_nodes, 1, 31)
        call odb%set_frame_descr(1, 'Increment: 1, Time: 1.0')
        call odb%set_nsfield( 1, '1:Displacement:Displacement in X',              displacement%at(:,  1))
        call odb%set_nsfield( 2, '1:Displacement:Displacement in Y',              displacement%at(:,  2))
        call odb%set_nsfield( 3, '1:Displacement:Displacement in Z',              displacement%at(:,  3))
        call odb%set_nsfield( 4, '1:Displacement:Magnitude of Displacement',      displacement%at(:,  4))
        call odb%set_nsfield( 5, '1:Reaction Force:Reaction Force in X',              reaction%at(:,  1))
        call odb%set_nsfield( 6, '1:Reaction Force:Reaction Force in Y',              reaction%at(:,  2))
        call odb%set_nsfield( 7, '1:Reaction Force:Reaction Force in Z',              reaction%at(:,  3))
        call odb%set_nsfield( 8, '1:Reaction Force:Magnitude of Reaction Force',      reaction%at(:,  4))
        call odb%set_nsfield( 9, '1:Strain:Component XX of Strain',          strain_extra_mesh%at(:,  1))
        call odb%set_nsfield(10, '1:Strain:Component YY of Strain',          strain_extra_mesh%at(:,  2))
        call odb%set_nsfield(11, '1:Strain:Component ZZ of Strain',          strain_extra_mesh%at(:,  3))
        call odb%set_nsfield(12, '1:Strain:Component YZ of Strain',          strain_extra_mesh%at(:,  4))
        call odb%set_nsfield(13, '1:Strain:Component ZX of Strain',          strain_extra_mesh%at(:,  5))
        call odb%set_nsfield(14, '1:Strain:Component XY of Strain',          strain_extra_mesh%at(:,  6))
        call odb%set_nsfield(15, '1:Strain:Max. Principal Value of Strain',  strain_extra_mesh%at(:,  7))
        call odb%set_nsfield(16, '1:Strain:Mid. Principal Value of Strain',  strain_extra_mesh%at(:,  8))
        call odb%set_nsfield(17, '1:Strain:Min. Principal Value of Strain',  strain_extra_mesh%at(:,  9))
        call odb%set_nsfield(18, '1:Strain:Major Principal Value of Strain', strain_extra_mesh%at(:, 10))
        call odb%set_nsfield(19, '1:Stress:Component XX of Stress',          stress_extra_mesh%at(:,  1))
        call odb%set_nsfield(20, '1:Stress:Component YY of Stress',          stress_extra_mesh%at(:,  2))
        call odb%set_nsfield(21, '1:Stress:Component ZZ of Stress',          stress_extra_mesh%at(:,  3))
        call odb%set_nsfield(22, '1:Stress:Component YZ of Stress',          stress_extra_mesh%at(:,  4))
        call odb%set_nsfield(23, '1:Stress:Component ZX of Stress',          stress_extra_mesh%at(:,  5))
        call odb%set_nsfield(24, '1:Stress:Component XY of Stress',          stress_extra_mesh%at(:,  6))
        call odb%set_nsfield(25, '1:Stress:Max. Principal Value of Stress',  stress_extra_mesh%at(:,  7))
        call odb%set_nsfield(26, '1:Stress:Mid. Principal Value of Stress',  stress_extra_mesh%at(:,  8))
        call odb%set_nsfield(27, '1:Stress:Min. Principal Value of Stress',  stress_extra_mesh%at(:,  9))
        call odb%set_nsfield(28, '1:Stress:Major Principal Value of Stress', stress_extra_mesh%at(:, 10))
        call odb%set_nsfield(29, '1:Stress:Tresca Equivalent Stress',        stress_extra_mesh%at(:, 11))
        call odb%set_nsfield(30, '1:Stress:Mises Equivalent Stress',         stress_extra_mesh%at(:, 12))
        call odb%set_nsfield(31, '1:Stress:Equivalent Pressure Stress',      stress_extra_mesh%at(:, 13))
    end function
    
end module
