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
        type(t_mdb), intent(in) :: mdb      ! model database
        type(t_sparse)          :: Kaa, Kab ! global stiffness matrix
        type(t_vector)          :: Pa       ! equivalent nodal loads vector
        type(t_vector)          :: Fe       ! external nodal forces
        type(t_vector)          :: Ua       ! unknown displacements
        type(t_vector)          :: Ub       ! prescribed nodal displacements
        type(t_vector)          :: R        ! reaction forces
        
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
        
        
        
        
        
        
        
        
        
        
        
        
    end subroutine
    
end module
