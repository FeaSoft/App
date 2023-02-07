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
        type(t_matrix)              :: displacements         ! displacements at the mesh nodes
        type(t_matrix)              :: reactions             ! reaction forces at the mesh nodes
        
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
        print '("Infinity norm of the out-of-balance forces vector (residual): ",E11.4)', maxval(abs(Fe%at(:) - Fa%at(:)))
        
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
        stress_extra_mesh = average(mdb%mesh, stress_extra_nodes, 12); if (allocated(stress_extra_nodes)) deallocate(stress_extra_nodes)
        
        ! convert global vectors to result matrices
        displacements = convert_vector(mdb%mesh%m_space, mdb%mesh%n_nodes, mdb%mesh%nodes, Ua, Ub)
        reactions     = convert_vector(mdb%mesh%m_space, mdb%mesh%n_nodes, mdb%mesh%nodes, new_vector(mdb%n_adofs), R)
        
        ! create output database
        odb = new_odb(mdb%mesh%n_nodes, 30)
        call odb%set_field( 1, 'Displacements:Displacement in X',            displacements%at(:,  1))
        call odb%set_field( 2, 'Displacements:Displacement in Y',            displacements%at(:,  2))
        call odb%set_field( 3, 'Displacements:Displacement in Z',            displacements%at(:,  3))
        call odb%set_field( 4, 'Displacements:Magnitude of Displacement',    displacements%at(:,  4))
        call odb%set_field( 5, 'Reaction Forces:Reaction Force in X',            reactions%at(:,  1))
        call odb%set_field( 6, 'Reaction Forces:Reaction Force in Y',            reactions%at(:,  2))
        call odb%set_field( 7, 'Reaction Forces:Reaction Force in Z',            reactions%at(:,  3))
        call odb%set_field( 8, 'Reaction Forces:Magnitude of Reaction Force',    reactions%at(:,  4))
        call odb%set_field( 9, 'Strain:Component XX of Strain',          strain_extra_mesh%at(:,  1))
        call odb%set_field(10, 'Strain:Component YY of Strain',          strain_extra_mesh%at(:,  2))
        call odb%set_field(11, 'Strain:Component ZZ of Strain',          strain_extra_mesh%at(:,  3))
        call odb%set_field(12, 'Strain:Component YZ of Strain',          strain_extra_mesh%at(:,  4))
        call odb%set_field(13, 'Strain:Component ZX of Strain',          strain_extra_mesh%at(:,  5))
        call odb%set_field(14, 'Strain:Component XY of Strain',          strain_extra_mesh%at(:,  6))
        call odb%set_field(15, 'Strain:Max. Principal Value of Strain',  strain_extra_mesh%at(:,  7))
        call odb%set_field(16, 'Strain:Mid. Principal Value of Strain',  strain_extra_mesh%at(:,  8))
        call odb%set_field(17, 'Strain:Min. Principal Value of Strain',  strain_extra_mesh%at(:,  9))
        call odb%set_field(18, 'Strain:Major Principal Value of Strain', strain_extra_mesh%at(:, 10))
        call odb%set_field(19, 'Stress:Component XX of Stress',          stress_extra_mesh%at(:,  1))
        call odb%set_field(20, 'Stress:Component YY of Stress',          stress_extra_mesh%at(:,  2))
        call odb%set_field(21, 'Stress:Component ZZ of Stress',          stress_extra_mesh%at(:,  3))
        call odb%set_field(22, 'Stress:Component YZ of Stress',          stress_extra_mesh%at(:,  4))
        call odb%set_field(23, 'Stress:Component ZX of Stress',          stress_extra_mesh%at(:,  5))
        call odb%set_field(24, 'Stress:Component XY of Stress',          stress_extra_mesh%at(:,  6))
        call odb%set_field(25, 'Stress:Max. Principal Value of Stress',  stress_extra_mesh%at(:,  7))
        call odb%set_field(26, 'Stress:Mid. Principal Value of Stress',  stress_extra_mesh%at(:,  8))
        call odb%set_field(27, 'Stress:Min. Principal Value of Stress',  stress_extra_mesh%at(:,  9))
        call odb%set_field(28, 'Stress:Major Principal Value of Stress', stress_extra_mesh%at(:, 10))
        call odb%set_field(29, 'Stress:von Mises',                       stress_extra_mesh%at(:, 11))
        call odb%set_field(30, 'Stress:Tresca',                          stress_extra_mesh%at(:, 12))
    end function
    
end module
