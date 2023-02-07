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
    subroutine static_analysis(mdb)
        ! procedure arguments
        type(t_mdb), intent(in) :: mdb ! model database
        
        ! additional variables
        type(t_sparse)              :: Kaa, Kab            ! global stiffness matrix
        type(t_vector)              :: Pa                  ! equivalent nodal loads vector
        type(t_vector)              :: Fe                  ! external nodal forces
        type(t_vector)              :: Ua                  ! unknown displacements
        type(t_vector)              :: Ub                  ! prescribed nodal displacements
        type(t_vector)              :: R                   ! reaction forces
        type(t_vector)              :: Fa, Fb              ! internal nodal forces
        type(t_matrix), allocatable :: strain_ips(:)       ! strain at the integration points (basic components)
        type(t_matrix), allocatable :: stress_ips(:)       ! stress at the integration points (basic components)
        type(t_matrix), allocatable :: strain_extra_ips(:) ! strain at the integration points (with extra components)
        type(t_matrix), allocatable :: stress_extra_ips(:) ! stress at the integration points (with extra components)
        
        ! allocate storage
        allocate(strain_ips(mdb%mesh%n_elements))
        allocate(stress_ips(mdb%mesh%n_elements))
        allocate(strain_extra_ips(mdb%mesh%n_elements))
        allocate(stress_extra_ips(mdb%mesh%n_elements))
        
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
        print '("Infinity norm of the out-of-balance forces vector (residual): ",E10.4)', maxval(abs(Fe%at(:) - Fa%at(:)))
        
        ! compute additional strain and stress measures (principal strains, principal stresses, and equivalent stresses)
        ! deallocate unused storage
        call extra_strain(strain_ips, strain_extra_ips); if (allocated(strain_ips)) deallocate(strain_ips)
        call extra_stress(stress_ips, stress_extra_ips); if (allocated(stress_ips)) deallocate(stress_ips)
        
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        ! DEALLOCATE STORAGE !!!!!!!!
        
    end subroutine
    
end module
